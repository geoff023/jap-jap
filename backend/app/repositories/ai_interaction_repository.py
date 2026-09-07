from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class AIInteractionRepository:
    """Lightweight usage log — per docs/AI.md, only enough context to know
    what was asked is stored (not full prompts/model output), so this
    collection never becomes a second copy of personal learner data."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["ai_interactions"]

    async def record(self, user_id: str, interaction_type: str, concept: str) -> None:
        await self._collection.insert_one(
            {
                "user_id": user_id,
                "interaction_type": interaction_type,
                "concept": concept,
                "created_at": datetime.now(timezone.utc),
            }
        )

    async def count_by_user(self, user_id: str) -> int:
        return await self._collection.count_documents({"user_id": user_id})

    async def list_by_user(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        cursor = self._collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("user_id")
