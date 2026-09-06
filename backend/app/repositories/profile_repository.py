from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class LearnerProfileRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["learner_profiles"]

    async def find_by_user_id(self, user_id: str) -> dict[str, Any] | None:
        return await self._collection.find_one({"user_id": user_id})

    async def upsert(
        self,
        user_id: str,
        fields: dict[str, Any],
        set_on_insert: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        await self._collection.update_one(
            {"user_id": user_id},
            {
                "$set": {**fields, "updated_at": now},
                "$setOnInsert": {"user_id": user_id, "created_at": now, **(set_on_insert or {})},
            },
            upsert=True,
        )
        profile = await self.find_by_user_id(user_id)
        assert profile is not None
        return profile

    async def increment_xp(self, user_id: str, amount: int) -> dict[str, Any] | None:
        """No-op (returns None) if the profile doesn't exist yet — never
        upserts here, since that would create a profile missing every other
        required field. Callers must ensure onboarding happened first."""
        await self._collection.update_one(
            {"user_id": user_id},
            {"$inc": {"xp": amount}, "$set": {"updated_at": datetime.now(timezone.utc)}},
        )
        return await self.find_by_user_id(user_id)

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("user_id", unique=True)
