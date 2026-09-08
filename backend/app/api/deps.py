from functools import lru_cache
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ai.base import AIService
from app.ai.gemini_service import GeminiService
from app.core.config import Settings, get_settings
from app.core.database import get_database
from app.core.security import decode_access_token
from app.repositories.achievement_repository import (
    AchievementRepository,
    UserAchievementRepository,
)
from app.repositories.activity_repository import ActivityRepository
from app.repositories.ai_interaction_repository import AIInteractionRepository
from app.repositories.conversation_repository import (
    ConversationMessageRepository,
    ConversationSessionRepository,
)
from app.repositories.grammar_repository import GrammarRepository
from app.repositories.kanji_repository import KanjiRepository
from app.repositories.mini_story_repository import MiniStoryRepository
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.review_schedule_repository import ReviewScheduleRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.repositories.speaking_repository import SpeakingAttemptRepository
from app.repositories.test_attempt_repository import TestAttemptRepository
from app.repositories.test_repository import TestRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.speech.base import SpeechToTextService
from app.speech.gemini_provider import GeminiSTTProvider

_bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserRepository:
    return UserRepository(db)


def get_profile_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> LearnerProfileRepository:
    return LearnerProfileRepository(db)


def get_vocabulary_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> VocabularyRepository:
    return VocabularyRepository(db)


def get_grammar_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> GrammarRepository:
    return GrammarRepository(db)


def get_kanji_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> KanjiRepository:
    return KanjiRepository(db)


def get_activity_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ActivityRepository:
    return ActivityRepository(db)


def get_question_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> QuestionRepository:
    return QuestionRepository(db)


def get_test_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> TestRepository:
    return TestRepository(db)


def get_test_attempt_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> TestAttemptRepository:
    return TestAttemptRepository(db)


def get_skill_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> LearnerSkillRepository:
    return LearnerSkillRepository(db)


def get_review_schedule_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ReviewScheduleRepository:
    return ReviewScheduleRepository(db)


def get_ai_interaction_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> AIInteractionRepository:
    return AIInteractionRepository(db)


def get_mini_story_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> MiniStoryRepository:
    return MiniStoryRepository(db)


def get_conversation_session_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ConversationSessionRepository:
    return ConversationSessionRepository(db)


def get_conversation_message_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ConversationMessageRepository:
    return ConversationMessageRepository(db)


def get_speaking_attempt_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> SpeakingAttemptRepository:
    return SpeakingAttemptRepository(db)


def get_achievement_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> AchievementRepository:
    return AchievementRepository(db)


def get_user_achievement_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> UserAchievementRepository:
    return UserAchievementRepository(db)


@lru_cache
def _build_gemini_service(api_key: str) -> GeminiService:
    return GeminiService(api_key)


def get_ai_service(settings: Settings = Depends(get_settings)) -> AIService:
    """Raises 503 rather than returning a service when no GEMINI_API_KEY is
    configured — the app as a whole must still start and run fine without
    one (see docs/AI.md); only these specific endpoints become unavailable."""
    if not settings.ai_enabled or settings.gemini_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features are not configured. Set GEMINI_API_KEY to enable them.",
        )
    return _build_gemini_service(settings.gemini_api_key)


@lru_cache
def _build_gemini_stt_provider(api_key: str) -> GeminiSTTProvider:
    return GeminiSTTProvider(api_key)


def get_stt_service(settings: Settings = Depends(get_settings)) -> SpeechToTextService:
    """Mirrors get_ai_service, but gated on STT_API_KEY rather than
    GEMINI_API_KEY — speech features are configured independently of the
    AI tutor/generation features, even though both currently talk to
    Gemini under the hood (see docs/AI.md)."""
    if not settings.stt_enabled or settings.stt_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Speech features are not configured. Set STT_API_KEY to enable them.",
        )
    return _build_gemini_stt_provider(settings.stt_api_key)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    users: UserRepository = Depends(get_user_repository),
) -> dict[str, Any]:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    try:
        user_id = decode_access_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise unauthorized from exc

    user = await users.find_by_id(user_id)
    if user is None:
        raise unauthorized
    return user
