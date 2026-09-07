from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_profile_repository, get_skill_repository
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.schemas.progress import ProgressResponse
from app.services.learner_model_service import LearnerModelService

router = APIRouter()


def _service(
    skills: LearnerSkillRepository = Depends(get_skill_repository),
    profiles: LearnerProfileRepository = Depends(get_profile_repository),
) -> LearnerModelService:
    return LearnerModelService(skills, profiles)


@router.get("", response_model=ProgressResponse)
async def get_progress(
    current_user: dict = Depends(get_current_user),
    service: LearnerModelService = Depends(_service),
) -> ProgressResponse:
    data = await service.get_progress(str(current_user["_id"]))
    return ProgressResponse(**data)
