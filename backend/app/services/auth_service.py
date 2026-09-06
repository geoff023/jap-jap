from typing import Any

from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self._users = user_repository

    async def register(self, email: str, password: str) -> dict[str, Any]:
        existing = await self._users.find_by_email(email)
        if existing is not None:
            raise EmailAlreadyRegisteredError(email)
        return await self._users.create(email, hash_password(password))

    async def authenticate(self, email: str, password: str) -> dict[str, Any]:
        user = await self._users.find_by_email(email)
        if user is None or not verify_password(password, user["hashed_password"]):
            raise InvalidCredentialsError()
        return user
