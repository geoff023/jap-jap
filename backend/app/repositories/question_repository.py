from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase


class QuestionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["questions"]

    async def find_by_id(self, question_id: str) -> dict[str, Any] | None:
        try:
            object_id = ObjectId(question_id)
        except InvalidId:
            return None
        return await self._collection.find_one({"_id": object_id})

    async def find_by_ids(self, ids: list[str]) -> list[dict[str, Any]]:
        object_ids = []
        for item_id in ids:
            try:
                object_ids.append(ObjectId(item_id))
            except InvalidId:
                continue
        return await self._collection.find({"_id": {"$in": object_ids}}).to_list(length=None)

    async def list_by_category(self, category: str) -> list[dict[str, Any]]:
        return await self._collection.find({"category": category}).to_list(length=None)

    async def create(self, document: dict[str, Any]) -> dict[str, Any]:
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def seed_if_empty(self, items: list[dict[str, Any]]) -> None:
        if await self._collection.count_documents({}) == 0 and items:
            await self._collection.insert_many(items)

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("category")
        await self._collection.create_index("level")
