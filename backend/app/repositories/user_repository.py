from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["users"]

    async def find_by_email(self, email: str) -> dict[str, Any] | None:
        return await self._collection.find_one({"email": email})

    async def find_by_id(self, user_id: str) -> dict[str, Any] | None:
        try:
            object_id = ObjectId(user_id)
        except InvalidId:
            return None
        return await self._collection.find_one({"_id": object_id})

    async def create(self, email: str, hashed_password: str) -> dict[str, Any]:
        document = {
            "email": email,
            "hashed_password": hashed_password,
            "created_at": datetime.now(timezone.utc),
        }
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("email", unique=True)
