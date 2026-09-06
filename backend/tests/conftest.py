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
