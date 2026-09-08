from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.profile import JLPTLevel


class SpeechTranscription(BaseModel):
    """A speech provider's structured output for one transcription request."""

    transcript: str = Field(max_length=500)


class SpeakingPromptPublic(BaseModel):
    key: str
    level: JLPTLevel
    target_text: str
    target_reading: str
    target_translation: str


class SubmitSpeakingAttemptResponse(BaseModel):
    transcript: str
    target_text: str
    correct: bool
    similarity: float
    xp_earned: int
    total_xp: int


class SpeakingAttemptSummary(BaseModel):
    id: str
    prompt_key: str
    level: JLPTLevel
    target_text: str
    transcript: str
    correct: bool
    similarity: float
    xp_earned: int
    created_at: datetime


def attempt_to_summary(doc: dict[str, Any]) -> SpeakingAttemptSummary:
    return SpeakingAttemptSummary(
        id=str(doc["_id"]),
        prompt_key=doc["prompt_key"],
        level=doc["level"],
        target_text=doc["target_text"],
        transcript=doc["transcript"],
        correct=doc["correct"],
        similarity=doc["similarity"],
        xp_earned=doc["xp_earned"],
        created_at=doc["created_at"],
    )
