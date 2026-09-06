from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_user_repository
from app.core.security import create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, user_to_public
from app.services.auth_service import (
    AuthService,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest, users: UserRepository = Depends(get_user_repository)
) -> TokenResponse:
    service = AuthService(users)
    try:
        user = await service.register(payload.email, payload.password)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        ) from exc

    token = create_access_token(str(user["_id"]))
    return TokenResponse(access_token=token, user=user_to_public(user))


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest, users: UserRepository = Depends(get_user_repository)
) -> TokenResponse:
    service = AuthService(users)
    try:
        user = await service.authenticate(payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        ) from exc

    token = create_access_token(str(user["_id"]))
    return TokenResponse(access_token=token, user=user_to_public(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: dict = Depends(get_current_user)) -> None:
    # Access tokens are short-lived stateless JWTs with no server-side session,
    # so there is nothing to invalidate yet. This endpoint stays protected and
    # semantically meaningful so the frontend has a real logout call to make,
    # and so a token blacklist can be added here later without an API change.
    return None
