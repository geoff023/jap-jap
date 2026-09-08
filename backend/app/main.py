from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.activities import router as activities_router
from app.api.ai import router as ai_router
from app.api.ai_generation import router as ai_generation_router
from app.api.auth import router as auth_router
from app.api.conversation import router as conversation_router
from app.api.grammar import router as grammar_router
from app.api.health import router as health_router
from app.api.mistakes import router as mistakes_router
from app.api.onboarding import router as onboarding_router
from app.api.profile import router as profile_router
from app.api.progress import router as progress_router
from app.api.recommendations import router as recommendations_router
from app.api.speech import router as speech_router
from app.api.tests import router as tests_router
from app.api.users import router as users_router
from app.api.vocabulary import router as vocabulary_router
from app.core.config import get_settings
from app.core.database import close_client, get_database
from app.core.seed_data import GRAMMAR_N5, VOCABULARY_N5
from app.core.test_seed_data import seed_test_engine
from app.repositories.activity_repository import ActivityRepository
from app.repositories.ai_interaction_repository import AIInteractionRepository
from app.repositories.conversation_repository import (
    ConversationMessageRepository,
    ConversationSessionRepository,
)
from app.repositories.grammar_repository import GrammarRepository
from app.repositories.mini_story_repository import MiniStoryRepository
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.repositories.speaking_repository import SpeakingAttemptRepository
from app.repositories.test_attempt_repository import TestAttemptRepository
from app.repositories.test_repository import TestRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vocabulary_repository import VocabularyRepository

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        db = get_database()
        await UserRepository(db).ensure_indexes()
        await LearnerProfileRepository(db).ensure_indexes()
        await ActivityRepository(db).ensure_indexes()

        vocabulary_repo = VocabularyRepository(db)
        await vocabulary_repo.ensure_indexes()
        await vocabulary_repo.seed_if_empty(VOCABULARY_N5)

        grammar_repo = GrammarRepository(db)
        await grammar_repo.ensure_indexes()
        await grammar_repo.seed_if_empty(GRAMMAR_N5)

        await QuestionRepository(db).ensure_indexes()
        await TestRepository(db).ensure_indexes()
        await TestAttemptRepository(db).ensure_indexes()
        await seed_test_engine(db)

        await LearnerSkillRepository(db).ensure_indexes()
        await AIInteractionRepository(db).ensure_indexes()
        await MiniStoryRepository(db).ensure_indexes()
        await ConversationSessionRepository(db).ensure_indexes()
        await ConversationMessageRepository(db).ensure_indexes()
        await SpeakingAttemptRepository(db).ensure_indexes()
    except Exception:
        # MongoDB may be unavailable (e.g. local dev without it running yet);
        # the app should still start, and /api/health reports the DB status.
        pass
    yield
    close_client()


app = FastAPI(title="JapJap API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(onboarding_router, prefix="/api/onboarding", tags=["onboarding"])
app.include_router(profile_router, prefix="/api/profile", tags=["profile"])
app.include_router(vocabulary_router, prefix="/api/vocabulary", tags=["vocabulary"])
app.include_router(grammar_router, prefix="/api/grammar", tags=["grammar"])
app.include_router(activities_router, prefix="/api/activities", tags=["activities"])
app.include_router(tests_router, prefix="/api/tests", tags=["tests"])
app.include_router(progress_router, prefix="/api/progress", tags=["progress"])
app.include_router(mistakes_router, prefix="/api/mistakes", tags=["mistakes"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
app.include_router(ai_generation_router, prefix="/api/ai", tags=["ai-generation"])
app.include_router(conversation_router, prefix="/api/conversation", tags=["conversation"])
app.include_router(speech_router, prefix="/api/speech", tags=["speech"])
app.include_router(recommendations_router, prefix="/api/recommendations", tags=["recommendations"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "JapJap API"}
