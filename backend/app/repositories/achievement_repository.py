from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class AchievementRepository:
    """The achievement catalog — seeded once from app/core/achievement_seed_data.py,
    read-only from the application's perspective otherwise."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["achievements"]

    async def list_all(self) -> list[dict[str, Any]]:
        cursor = self._collection.find({}).sort("_seed_order", 1)
        return await cursor.to_list(length=None)

    async def seed_if_empty(self, items: list[dict[str, Any]]) -> None:
        if await self._collection.count_documents({}) == 0 and items:
            await self._collection.insert_many(
                [{**item, "_seed_order": index} for index, item in enumerate(items)]
            )

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("key", unique=True)


class UserAchievementRepository:
    """Per-user unlock records. `unlock` is idempotent — calling it again for
    an already-unlocked achievement is a no-op, so `unlocked_at` never
    shifts forward on a later recheck."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["user_achievements"]

    async def list_by_user(self, user_id: str) -> list[dict[str, Any]]:
        return await self._collection.find({"user_id": user_id}).to_list(length=None)

    async def unlock(self, user_id: str, achievement_key: str, when: datetime) -> None:
        await self._collection.update_one(
            {"user_id": user_id, "achievement_key": achievement_key},
            {
                "$setOnInsert": {
                    "user_id": user_id,
                    "achievement_key": achievement_key,
                    "unlocked_at": when,
                }
            },
            upsert=True,
        )

    async def ensure_indexes(self) -> None:
        await self._collection.create_index([("user_id", 1), ("achievement_key", 1)], unique=True)
        await self._collection.create_index("user_id")
