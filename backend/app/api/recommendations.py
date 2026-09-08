from fastapi import APIRouter, Depends

from app.api.deps import get_conversation_session_repository, get_current_user, get_skill_repository
from app.repositories.conversation_repository import ConversationSessionRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.schemas.recommendations import RecommendationsResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter()


def _service(
    skills: LearnerSkillRepository = Depends(get_skill_repository),
    conversations: ConversationSessionRepository = Depends(get_conversation_session_repository),
) -> RecommendationService:
    return RecommendationService(skills, conversations)


@router.get("", response_model=RecommendationsResponse)
async def get_recommendations(
    current_user: dict = Depends(get_current_user),
    service: RecommendationService = Depends(_service),
) -> RecommendationsResponse:
    recommendations = await service.get_recommendations(str(current_user["_id"]))
    return RecommendationsResponse(recommendations=recommendations)
