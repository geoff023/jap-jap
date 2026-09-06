from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    """Return a lazily-created, shared Motor client.

    Motor's client is non-blocking to construct — actual connection attempts
    only happen when a command is issued — so this never raises even if
    MongoDB is unreachable.
    """
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=settings.mongo_server_selection_timeout_ms,
        )
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client().get_default_database()


def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
