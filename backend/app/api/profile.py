from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_profile_repository
from app.repositories.profile_repository import LearnerProfileRepository
from app.schemas.profile import LearnerProfilePublic, ProfileUpdateRequest, profile_to_public
from app.services.profile_service import ProfileNotFoundError, ProfileService

router = APIRouter()


@router.get("", response_model=LearnerProfilePublic)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    profiles: LearnerProfileRepository = Depends(get_profile_repository),
) -> LearnerProfilePublic:
    profile = await profiles.find_by_user_id(str(current_user["_id"]))
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Onboarding not completed yet"
        )
    return profile_to_public(profile)


@router.patch("", response_model=LearnerProfilePublic)
async def update_profile(
    payload: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
    profiles: LearnerProfileRepository = Depends(get_profile_repository),
) -> LearnerProfilePublic:
    updates = payload.model_dump(exclude_unset=True, mode="json")
    service = ProfileService(profiles)
    try:
        profile = await service.update_profile(str(current_user["_id"]), updates)
    except ProfileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Onboarding not completed yet"
        ) from exc
    return profile_to_public(profile)
