from typing import Any

from app.repositories.profile_repository import LearnerProfileRepository
from app.schemas.profile import OnboardingRequest


class ProfileNotFoundError(Exception):
    pass


class ProfileService:
    def __init__(self, profiles: LearnerProfileRepository):
        self._profiles = profiles

    async def get_profile(self, user_id: str) -> dict[str, Any] | None:
        return await self._profiles.find_by_user_id(user_id)

    async def complete_onboarding(self, user_id: str, payload: OnboardingRequest) -> dict[str, Any]:
        return await self._profiles.upsert(
            user_id,
            {
                "goals": [goal.value for goal in payload.goals],
                "experience": payload.experience.value,
                "preferred_level": payload.preferred_level.value,
                "jlpt_target": payload.jlpt_target.value if payload.jlpt_target else None,
                # No assessment data exists yet at onboarding time. Later
                # phases (test engine / learner model) are what earn the
                # right to set this — never fabricated.
                "estimated_level": None,
                "onboarding_completed": True,
            },
        )

    async def update_profile(self, user_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Apply a partial update. `updates` must already be plain JSON values
        (e.g. from `ProfileUpdateRequest.model_dump(exclude_unset=True, mode="json")`),
        not enum members."""
        existing = await self._profiles.find_by_user_id(user_id)
        if existing is None:
            raise ProfileNotFoundError(user_id)

        return await self._profiles.upsert(user_id, updates)
