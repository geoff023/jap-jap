from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_profile_repository
from app.repositories.profile_repository import LearnerProfileRepository
from app.schemas.profile import LearnerProfilePublic, OnboardingRequest, profile_to_public
from app.services.profile_service import ProfileService

router = APIRouter()


@router.post("", response_model=LearnerProfilePublic)
async def complete_onboarding(
    payload: OnboardingRequest,
    current_user: dict = Depends(get_current_user),
    profiles: LearnerProfileRepository = Depends(get_profile_repository),
) -> LearnerProfilePublic:
    service = ProfileService(profiles)
    profile = await service.complete_onboarding(str(current_user["_id"]), payload)
    return profile_to_public(profile)
