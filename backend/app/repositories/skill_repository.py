from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class LearnerSkillRepository:
    """Tracks per-(user, category, concept) correct/incorrect counts.

    This is the single source of truth for skill mastery, the mistakes
    list, and estimated JLPT readiness — all derived by aggregating these
    documents, never fabricated.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["learner_skills"]

    async def record_result(
        self, user_id: str, category: str, concept: str, correct: bool, occurred_at: datetime
    ) -> None:
        field = "correct_count" if correct else "incorrect_count"
        await self._collection.update_one(
            {"user_id": user_id, "category": category, "concept": concept},
            {
                "$inc": {field: 1},
                "$set": {"last_seen": occurred_at},
                "$setOnInsert": {
                    "user_id": user_id,
                    "category": category,
                    "concept": concept,
                    "created_at": occurred_at,
                },
            },
            upsert=True,
        )

    async def list_by_user(self, user_id: str) -> list[dict[str, Any]]:
        return await self._collection.find({"user_id": user_id}).to_list(length=None)

    async def list_mistakes(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        cursor = (
            self._collection.find({"user_id": user_id, "incorrect_count": {"$gt": 0}})
            .sort("incorrect_count", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def ensure_indexes(self) -> None:
        await self._collection.create_index(
            [("user_id", 1), ("category", 1), ("concept", 1)], unique=True
        )
        await self._collection.create_index("user_id")
