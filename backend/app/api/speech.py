from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.deps import (
    get_current_user,
    get_profile_repository,
    get_skill_repository,
    get_speaking_attempt_repository,
    get_stt_service,
)
from app.core.speaking_data import list_prompts as _list_prompts
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.repositories.speaking_repository import SpeakingAttemptRepository
from app.schemas.speech import (
    SpeakingAttemptSummary,
    SpeakingPromptPublic,
    SubmitSpeakingAttemptResponse,
    attempt_to_summary,
)
from app.services.speaking_service import (
    ProfileRequiredError,
    PromptNotFoundError,
    SpeakingService,
)
from app.speech.base import SpeechServiceError, SpeechToTextService

router = APIRouter()

# Keeps a bad/oversized upload from ever reaching the (paid, slower) speech
# provider — rejected here with 422 before SpeakingService is even called.
MAX_AUDIO_BYTES = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {
    "audio/webm",
    "audio/wav",
    "audio/wave",
    "audio/x-wav",
    "audio/mp3",
    "audio/mpeg",
    "audio/ogg",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
}


def _service(
    stt: SpeechToTextService = Depends(get_stt_service),
    attempts: SpeakingAttemptRepository = Depends(get_speaking_attempt_repository),
    profiles: LearnerProfileRepository = Depends(get_profile_repository),
    skills: LearnerSkillRepository = Depends(get_skill_repository),
) -> SpeakingService:
    return SpeakingService(stt, attempts, profiles, skills)


@router.get("/prompts", response_model=list[SpeakingPromptPublic])
async def list_prompts(
    level: str | None = None,
    current_user: dict = Depends(get_current_user),
) -> list[SpeakingPromptPublic]:
    return [SpeakingPromptPublic(**p) for p in _list_prompts(level)]


@router.get("/attempts", response_model=list[SpeakingAttemptSummary])
async def list_attempts(
    current_user: dict = Depends(get_current_user),
    attempts: SpeakingAttemptRepository = Depends(get_speaking_attempt_repository),
) -> list[SpeakingAttemptSummary]:
    docs = await attempts.list_by_user(str(current_user["_id"]))
    return [attempt_to_summary(d) for d in docs]


@router.post("/attempts", response_model=SubmitSpeakingAttemptResponse)
async def submit_attempt(
    prompt_key: str = Form(...),
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    service: SpeakingService = Depends(_service),
) -> SubmitSpeakingAttemptResponse:
    if audio.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported audio format.",
        )

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No audio data received."
        )
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Audio file is too large."
        )

    try:
        result = await service.submit_attempt(
            str(current_user["_id"]), prompt_key, audio_bytes, audio.content_type
        )
    except ProfileRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Onboarding not completed yet"
        ) from exc
    except PromptNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
        ) from exc
    except SpeechServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not transcribe your recording. Please try again.",
        ) from exc

    return SubmitSpeakingAttemptResponse(
        transcript=result["transcript"],
        target_text=result["target_text"],
        correct=result["correct"],
        similarity=result["similarity"],
        xp_earned=result["xp_earned"],
        total_xp=result["total_xp"],
    )
