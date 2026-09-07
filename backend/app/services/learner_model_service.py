from typing import Any

from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.schemas.progress import TRACKED_CATEGORIES

# Below this many combined vocabulary+grammar attempts, an "estimated
# readiness" figure would be more noise than signal — report "not enough
# data yet" instead of a shaky number.
MIN_ATTEMPTS_FOR_READINESS = 5


class LearnerModelService:
    def __init__(self, skills: LearnerSkillRepository, profiles: LearnerProfileRepository):
        self._skills = skills
        self._profiles = profiles

    async def get_progress(self, user_id: str) -> dict[str, Any]:
        skill_docs = await self._skills.list_by_user(user_id)

        by_category: dict[str, list[dict[str, Any]]] = {c: [] for c in TRACKED_CATEGORIES}
        for doc in skill_docs:
            by_category.setdefault(doc["category"], []).append(doc)

        category_progress = []
        total_correct = 0
        total_attempts = 0
        for category in TRACKED_CATEGORIES:
            docs = by_category.get(category, [])
            correct = sum(d.get("correct_count", 0) for d in docs)
            incorrect = sum(d.get("incorrect_count", 0) for d in docs)
            attempts = correct + incorrect
            has_data = attempts > 0

            category_progress.append(
                {
                    "category": category,
                    "mastery": (correct / attempts) if has_data else None,
                    "concepts_tracked": len(docs),
                    "has_data": has_data,
                }
            )
            if has_data:
                total_correct += correct
                total_attempts += attempts

        overall_has_data = total_attempts > 0

        profile = await self._profiles.find_by_user_id(user_id)
        jlpt_target = profile.get("jlpt_target") if profile else None

        readiness_has_data = (
            jlpt_target is not None and total_attempts >= MIN_ATTEMPTS_FOR_READINESS
        )

        return {
            "overall": {
                "mastery": (total_correct / total_attempts) if overall_has_data else None,
                "has_data": overall_has_data,
            },
            "skills": category_progress,
            "estimated_jlpt_readiness": {
                "jlpt_target": jlpt_target,
                # Deliberately the same pooled vocabulary+grammar accuracy as
                # "overall" — an honest, simple proxy given only N5 content
                # exists so far, not a real predictive model.
                "score": (total_correct / total_attempts) if readiness_has_data else None,
                "has_data": readiness_has_data,
            },
        }

    async def list_mistakes(self, user_id: str) -> list[dict[str, Any]]:
        return await self._skills.list_mistakes(user_id)
