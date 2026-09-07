from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase


class MiniStoryRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["mini_stories"]

    async def create(self, document: dict[str, Any]) -> dict[str, Any]:
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def find_by_id(self, story_id: str) -> dict[str, Any] | None:
        try:
            object_id = ObjectId(story_id)
        except InvalidId:
            return None
        return await self._collection.find_one({"_id": object_id})

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("level")
        await self._collection.create_index("generated_by_user_id")
