import difflib
import re
from datetime import datetime, timezone
from typing import Any

from app.core.speaking_data import get_prompt, list_prompts
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.repositories.speaking_repository import SpeakingAttemptRepository
from app.speech.base import SpeechToTextService

XP_PER_CORRECT = 10

# A transcript rarely matches the target byte-for-byte even when the
# pronunciation was fine (STT noise, an optional trailing particle heard or
# not) — a similarity ratio threshold is more forgiving than exact match
# while still requiring most of the phrase to be right.
SIMILARITY_THRESHOLD = 0.8

_PUNCTUATION_RE = re.compile(r"[\s。、！？!?]")


def _normalize(text: str) -> str:
    return _PUNCTUATION_RE.sub("", text)


class ProfileRequiredError(Exception):
    """Raised when a learner tries to earn XP before completing onboarding."""


class PromptNotFoundError(Exception):
    pass


class SpeakingService:
    def __init__(
        self,
        stt: SpeechToTextService,
        attempts: SpeakingAttemptRepository,
        profiles: LearnerProfileRepository,
        skills: LearnerSkillRepository,
    ):
        self._stt = stt
        self._attempts = attempts
        self._profiles = profiles
        self._skills = skills

    def list_prompts(self, level: str | None) -> list[dict[str, Any]]:
        return list_prompts(level)

    async def list_attempts(self, user_id: str) -> list[dict[str, Any]]:
        return await self._attempts.list_by_user(user_id)

    async def submit_attempt(
        self, user_id: str, prompt_key: str, audio_bytes: bytes, mime_type: str
    ) -> dict[str, Any]:
        profile = await self._profiles.find_by_user_id(user_id)
        if profile is None:
            raise ProfileRequiredError(user_id)

        try:
            prompt = get_prompt(prompt_key)
        except KeyError as exc:
            raise PromptNotFoundError(prompt_key) from exc

        transcription = await self._stt.transcribe(audio_bytes, mime_type)

        target_normalized = _normalize(prompt["target_text"])
        transcript_normalized = _normalize(transcription.transcript)
        similarity = difflib.SequenceMatcher(None, target_normalized, transcript_normalized).ratio()
        is_correct = similarity >= SIMILARITY_THRESHOLD

        xp_earned = XP_PER_CORRECT if is_correct else 0
        now = datetime.now(timezone.utc)

        await self._attempts.create(
            {
                "user_id": user_id,
                "prompt_key": prompt_key,
                "level": prompt["level"],
                "target_text": prompt["target_text"],
                "transcript": transcription.transcript,
                "correct": is_correct,
                "similarity": similarity,
                "xp_earned": xp_earned,
                "created_at": now,
            }
        )

        await self._skills.record_result(user_id, "speaking", prompt_key, is_correct, now)
        updated_profile = await self._profiles.increment_xp(user_id, xp_earned)
        assert updated_profile is not None

        return {
            "transcript": transcription.transcript,
            "target_text": prompt["target_text"],
            "correct": is_correct,
            "similarity": similarity,
            "xp_earned": xp_earned,
            "total_xp": updated_profile["xp"],
        }
