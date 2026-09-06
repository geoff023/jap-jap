from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.auth import UserPublic, user_to_public

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: dict = Depends(get_current_user)) -> UserPublic:
    return user_to_public(current_user)
