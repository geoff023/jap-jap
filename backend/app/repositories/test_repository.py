from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase


class TestRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["tests"]

    async def list_all(self) -> list[dict[str, Any]]:
        return await self._collection.find({}).to_list(length=None)

    async def find_by_id(self, test_id: str) -> dict[str, Any] | None:
        try:
            object_id = ObjectId(test_id)
        except InvalidId:
            return None
        return await self._collection.find_one({"_id": object_id})

    async def count(self) -> int:
        return await self._collection.count_documents({})

    async def seed_if_empty(self, items: list[dict[str, Any]]) -> None:
        if await self.count() == 0 and items:
            await self._collection.insert_many(items)

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("category")
        await self._collection.create_index("level")
