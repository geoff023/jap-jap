import os

import pytest_asyncio

# Set before any `app.*` module is imported so Settings picks up a dedicated
# test database instead of the local dev one. A real MongoDB instance is
# still required (locally: docker compose up -d mongo; CI: a service
# container) — auth tests exercise real database behaviour, not a mock.
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/japjap_test")


@pytest_asyncio.fixture(autouse=True)
async def reset_database():
    """Give each test a Motor client bound to its own event loop.

    pytest-asyncio runs each test in a fresh event loop, but the app's Motor
    client is a lazily-created singleton — without resetting it here, a
    client created in one test's loop gets reused (and fails) once that loop
    closes. Also clears the users collection between tests for isolation.
    """
    from app.core.database import close_client, get_client

    close_client()
    yield
    db = get_client().get_default_database()
    await db["users"].delete_many({})
    await db["learner_profiles"].delete_many({})
    await db["learning_activities"].delete_many({})
    await db["test_attempts"].delete_many({})
    await db["learner_skills"].delete_many({})
    await db["ai_interactions"].delete_many({})
    await db["mini_stories"].delete_many({})
    await db["conversation_sessions"].delete_many({})
    await db["conversation_messages"].delete_many({})
    # AI-generated questions are per-test state, unlike the seeded ones —
    # only clear the ones this test run could have created.
    await db["questions"].delete_many({"source": "ai_generated"})
    # vocabulary/grammar_concepts/questions (seeded)/tests are shared
    # reference content, not per-test state — left in place so
    # `seed_content` only inserts once per test session instead of
    # reseeding before every test.
    close_client()


@pytest_asyncio.fixture
async def client():
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client):
    """Register a fresh user and return Authorization headers for it."""
    response = await client.post(
        "/api/auth/register",
        json={"email": "profile-owner@example.com", "password": "supersecret1"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def onboarded_auth_headers(client, auth_headers):
    """Like `auth_headers`, but also completes onboarding — required before
    any XP-earning activity endpoint will accept requests."""
    await client.post(
        "/api/onboarding",
        json={
            "goals": ["jlpt"],
            "experience": "knows_hiragana",
            "preferred_level": "N5",
            "jlpt_target": "N5",
        },
        headers=auth_headers,
    )
    return auth_headers


@pytest_asyncio.fixture
async def seed_content():
    """Seed the N5 vocabulary/grammar content if not already present.

    App startup normally does this (see app/main.py's lifespan), but
    httpx's ASGITransport doesn't trigger lifespan events, so tests seed
    explicitly. Cheap to call from every activity test: seed_if_empty is a
    no-op once the first test in the session has seeded it (these
    collections aren't cleared between tests — see reset_database above).
    """
    from app.core.database import get_database
    from app.core.seed_data import GRAMMAR_N5, VOCABULARY_N5
    from app.repositories.grammar_repository import GrammarRepository
    from app.repositories.vocabulary_repository import VocabularyRepository

    db = get_database()
    await VocabularyRepository(db).seed_if_empty(VOCABULARY_N5)
    await GrammarRepository(db).seed_if_empty(GRAMMAR_N5)


@pytest_asyncio.fixture
async def seed_tests():
    """Seed the Question/Test engine content if not already present (same
    ASGITransport-doesn't-run-lifespan caveat as `seed_content` above)."""
    from app.core.database import get_database
    from app.core.test_seed_data import seed_test_engine

    await seed_test_engine(get_database())


@pytest_asyncio.fixture
async def fake_ai_service():
    """Override the app's real get_ai_service dependency with a fake for the
    duration of one test — automated tests must never call the real Gemini
    API. Yields the fake so a test can inspect `.calls` or flip
    `.should_fail`."""
    from app.api.deps import get_ai_service
    from app.main import app
    from tests.fakes import FakeAIService

    fake = FakeAIService()
    app.dependency_overrides[get_ai_service] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_ai_service, None)
