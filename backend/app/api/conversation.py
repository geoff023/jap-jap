from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.base import AIService, AIServiceError
from app.api.deps import (
    get_ai_service,
    get_conversation_message_repository,
    get_conversation_session_repository,
    get_current_user,
    get_profile_repository,
)
from app.repositories.conversation_repository import (
    ConversationMessageRepository,
    ConversationSessionRepository,
)
from app.repositories.profile_repository import LearnerProfileRepository
from app.schemas.conversation import (
    ConversationSessionDetail,
    ConversationSessionSummary,
    ScenarioPublic,
    SendMessageRequest,
    SendMessageResponse,
    StartConversationRequest,
    session_to_detail,
    session_to_summary,
)
from app.services.conversation_service import (
    ConversationService,
    ProfileRequiredError,
    SessionNotFoundError,
)

router = APIRouter()


def _service(
    ai: AIService = Depends(get_ai_service),
    sessions: ConversationSessionRepository = Depends(get_conversation_session_repository),
    messages: ConversationMessageRepository = Depends(get_conversation_message_repository),
    profiles: LearnerProfileRepository = Depends(get_profile_repository),
) -> ConversationService:
    return ConversationService(ai, sessions, messages, profiles)


def _onboarding_required() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Onboarding not completed yet"
    )


def _session_not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


# Note: this router doesn't depend on get_ai_service for GET /scenarios,
# /sessions, or /sessions/{id} — those never call Gemini, so they must stay
# available even when GEMINI_API_KEY isn't configured. Only starting a
# session and sending a message touch the AI service.


@router.get("/scenarios", response_model=list[ScenarioPublic])
async def list_scenarios(
    current_user: dict = Depends(get_current_user),
) -> list[ScenarioPublic]:
    from app.core.conversation_data import list_scenarios as _list_scenarios

    return [ScenarioPublic(**s) for s in _list_scenarios()]


@router.get("/sessions", response_model=list[ConversationSessionSummary])
async def list_sessions(
    current_user: dict = Depends(get_current_user),
    sessions: ConversationSessionRepository = Depends(get_conversation_session_repository),
) -> list[ConversationSessionSummary]:
    docs = await sessions.list_by_user(str(current_user["_id"]))
    return [session_to_summary(d) for d in docs]


@router.get("/sessions/{session_id}", response_model=ConversationSessionDetail)
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    sessions: ConversationSessionRepository = Depends(get_conversation_session_repository),
    messages: ConversationMessageRepository = Depends(get_conversation_message_repository),
) -> ConversationSessionDetail:
    session = await sessions.find_by_id(session_id)
    if session is None or session["user_id"] != str(current_user["_id"]):
        raise _session_not_found()
    message_docs = await messages.list_by_session(session_id)
    return session_to_detail(session, message_docs)


@router.post("/sessions", response_model=ConversationSessionDetail)
async def start_session(
    payload: StartConversationRequest,
    current_user: dict = Depends(get_current_user),
    service: ConversationService = Depends(_service),
) -> ConversationSessionDetail:
    try:
        result = await service.start_session(
            str(current_user["_id"]), payload.scenario.value, payload.level.value
        )
    except ProfileRequiredError as exc:
        raise _onboarding_required() from exc
    return session_to_detail(result["session"], result["messages"])


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: str,
    payload: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
    service: ConversationService = Depends(_service),
) -> SendMessageResponse:
    try:
        result = await service.send_message(str(current_user["_id"]), session_id, payload.content)
    except ProfileRequiredError as exc:
        raise _onboarding_required() from exc
    except SessionNotFoundError as exc:
        raise _session_not_found() from exc
    except AIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The character couldn't respond. Please try again.",
        ) from exc
    return SendMessageResponse(
        user_message=result["user_message"],
        character_message=result["character_message"],
        xp_earned=result["xp_earned"],
        total_xp=result["total_xp"],
    )
