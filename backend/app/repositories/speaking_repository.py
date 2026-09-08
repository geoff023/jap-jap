from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class SpeakingAttemptRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["speaking_attempts"]

    async def create(self, document: dict[str, Any]) -> dict[str, Any]:
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def list_by_user(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        cursor = self._collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def count_by_user(self, user_id: str) -> int:
        return await self._collection.count_documents({"user_id": user_id})

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("user_id")
