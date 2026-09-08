from datetime import datetime
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase


class ConversationSessionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["conversation_sessions"]

    async def create(self, document: dict[str, Any]) -> dict[str, Any]:
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def find_by_id(self, session_id: str) -> dict[str, Any] | None:
        try:
            object_id = ObjectId(session_id)
        except InvalidId:
            return None
        return await self._collection.find_one({"_id": object_id})

    async def list_by_user(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        cursor = (
            self._collection.find({"user_id": user_id}).sort("last_message_at", -1).limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def count_by_user(self, user_id: str) -> int:
        return await self._collection.count_documents({"user_id": user_id})

    async def touch(self, session_id: str, when: datetime, increment: int) -> None:
        await self._collection.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"last_message_at": when}, "$inc": {"message_count": increment}},
        )

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("user_id")


class ConversationMessageRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["conversation_messages"]

    async def create(self, document: dict[str, Any]) -> dict[str, Any]:
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def list_by_session(self, session_id: str, limit: int = 200) -> list[dict[str, Any]]:
        cursor = (
            self._collection.find({"session_id": session_id}).sort("created_at", 1).limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("session_id")
