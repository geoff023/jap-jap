from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import (
    get_activity_repository,
    get_current_user,
    get_grammar_repository,
    get_profile_repository,
    get_vocabulary_repository,
)
from app.repositories.activity_repository import ActivityRepository
from app.repositories.grammar_repository import GrammarRepository
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.schemas.activity import (
    ActivityCategory,
    FlashcardCompleteRequest,
    FlashcardCompleteResponse,
    QuizResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
)
from app.schemas.profile import JLPTLevel
from app.services.activity_service import (
    ActivityService,
    NotEnoughContentError,
    ProfileRequiredError,
)

router = APIRouter()


def _service(
    vocabulary: VocabularyRepository = Depends(get_vocabulary_repository),
    grammar: GrammarRepository = Depends(get_grammar_repository),
    activities: ActivityRepository = Depends(get_activity_repository),
    profiles: LearnerProfileRepository = Depends(get_profile_repository),
) -> ActivityService:
    return ActivityService(vocabulary, grammar, activities, profiles)


@router.get("/quiz", response_model=QuizResponse)
async def get_quiz(
    category: ActivityCategory,
    level: JLPTLevel,
    size: int = Query(default=5, ge=1, le=20),
    current_user: dict = Depends(get_current_user),
    service: ActivityService = Depends(_service),
) -> QuizResponse:
    try:
        questions = await service.generate_quiz(category, level, size)
    except NotEnoughContentError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return QuizResponse(category=category, level=level, questions=questions)


@router.post("/quiz/submit", response_model=QuizSubmitResponse)
async def submit_quiz(
    payload: QuizSubmitRequest,
    current_user: dict = Depends(get_current_user),
    service: ActivityService = Depends(_service),
) -> QuizSubmitResponse:
    try:
        result = await service.submit_quiz(
            str(current_user["_id"]), payload.category, payload.level, payload.answers
        )
    except ProfileRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Onboarding not completed yet"
        ) from exc
    return QuizSubmitResponse(**result)


@router.post("/flashcards/complete", response_model=FlashcardCompleteResponse)
async def complete_flashcards(
    payload: FlashcardCompleteRequest,
    current_user: dict = Depends(get_current_user),
    service: ActivityService = Depends(_service),
) -> FlashcardCompleteResponse:
    try:
        result = await service.complete_flashcards(
            str(current_user["_id"]), payload.category, payload.level, payload.reviewed
        )
    except ProfileRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Onboarding not completed yet"
        ) from exc
    return FlashcardCompleteResponse(**result)
