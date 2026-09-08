from fastapi import APIRouter, Depends

from app.api.deps import (
    get_achievement_repository,
    get_activity_repository,
    get_conversation_session_repository,
    get_current_user,
    get_profile_repository,
    get_skill_repository,
    get_speaking_attempt_repository,
    get_test_attempt_repository,
    get_user_achievement_repository,
)
from app.repositories.achievement_repository import AchievementRepository, UserAchievementRepository
from app.repositories.activity_repository import ActivityRepository
from app.repositories.conversation_repository import ConversationSessionRepository
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.repositories.speaking_repository import SpeakingAttemptRepository
from app.repositories.test_attempt_repository import TestAttemptRepository
from app.schemas.achievements import AchievementPublic, achievement_to_public
from app.services.achievement_service import AchievementService

router = APIRouter()


def _service(
    achievements: AchievementRepository = Depends(get_achievement_repository),
    user_achievements: UserAchievementRepository = Depends(get_user_achievement_repository),
    profiles: LearnerProfileRepository = Depends(get_profile_repository),
    activities: ActivityRepository = Depends(get_activity_repository),
    tests: TestAttemptRepository = Depends(get_test_attempt_repository),
    conversations: ConversationSessionRepository = Depends(get_conversation_session_repository),
    speaking: SpeakingAttemptRepository = Depends(get_speaking_attempt_repository),
    skills: LearnerSkillRepository = Depends(get_skill_repository),
) -> AchievementService:
    return AchievementService(
        achievements,
        user_achievements,
        profiles,
        activities,
        tests,
        conversations,
        speaking,
        skills,
    )


@router.get("", response_model=list[AchievementPublic])
async def list_achievements(
    current_user: dict = Depends(get_current_user),
    service: AchievementService = Depends(_service),
) -> list[AchievementPublic]:
    results = await service.get_achievements(str(current_user["_id"]))
    return [achievement_to_public(r["definition"], r["unlocked_at"]) for r in results]
