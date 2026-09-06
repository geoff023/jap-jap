from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.security import decode_access_token
from app.repositories.activity_repository import ActivityRepository
from app.repositories.grammar_repository import GrammarRepository
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vocabulary_repository import VocabularyRepository

_bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserRepository:
    return UserRepository(db)


def get_profile_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> LearnerProfileRepository:
    return LearnerProfileRepository(db)


def get_vocabulary_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> VocabularyRepository:
    return VocabularyRepository(db)


def get_grammar_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> GrammarRepository:
    return GrammarRepository(db)


def get_activity_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ActivityRepository:
    return ActivityRepository(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    users: UserRepository = Depends(get_user_repository),
) -> dict[str, Any]:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    try:
        user_id = decode_access_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise unauthorized from exc

    user = await users.find_by_id(user_id)
    if user is None:
        raise unauthorized
    return user
