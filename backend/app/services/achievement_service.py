from datetime import datetime, timezone
from typing import Any

from app.repositories.achievement_repository import AchievementRepository, UserAchievementRepository
from app.repositories.activity_repository import ActivityRepository
from app.repositories.conversation_repository import ConversationSessionRepository
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.repositories.speaking_repository import SpeakingAttemptRepository
from app.repositories.test_attempt_repository import TestAttemptRepository

MIN_ATTEMPTS_FOR_MASTERY_CHECK = 5
PERFECTIONIST_THRESHOLD = 0.9
WELL_ROUNDED_CATEGORIES = {"vocabulary", "grammar", "kanji", "reading", "speaking", "conversation"}


class AchievementService:
    """Deterministic, no-AI milestone detection — same "backend decides"
    rule as recommendations (Phase 10). Checks are computed fresh from
    existing collections on every call and any newly-met achievement is
    unlocked (persisted with a stable unlocked_at) at that moment;
    already-unlocked achievements are never re-evaluated or re-timestamped.
    """

    def __init__(
        self,
        achievements: AchievementRepository,
        user_achievements: UserAchievementRepository,
        profiles: LearnerProfileRepository,
        activities: ActivityRepository,
        tests: TestAttemptRepository,
        conversations: ConversationSessionRepository,
        speaking: SpeakingAttemptRepository,
        skills: LearnerSkillRepository,
    ):
        self._achievements = achievements
        self._user_achievements = user_achievements
        self._profiles = profiles
        self._activities = activities
        self._tests = tests
        self._conversations = conversations
        self._speaking = speaking
        self._skills = skills

    async def get_achievements(self, user_id: str) -> list[dict[str, Any]]:
        catalog = await self._achievements.list_all()

        profile = await self._profiles.find_by_user_id(user_id)
        xp = profile["xp"] if profile else 0

        activity_count = await self._activities.count_by_user(user_id)
        test_count = await self._tests.count_by_user(user_id)
        conversation_count = await self._conversations.count_by_user(user_id)
        speaking_count = await self._speaking.count_by_user(user_id)

        skill_docs = await self._skills.list_by_user(user_id)
        by_category: dict[str, list[dict[str, Any]]] = {}
        for doc in skill_docs:
            by_category.setdefault(doc["category"], []).append(doc)

        mastery_by_category: dict[str, tuple[float, int]] = {}
        for category, docs in by_category.items():
            correct = sum(d.get("correct_count", 0) for d in docs)
            incorrect = sum(d.get("incorrect_count", 0) for d in docs)
            attempts = correct + incorrect
            mastery_by_category[category] = (correct / attempts if attempts else 0.0, attempts)

        tried_categories = set(by_category.keys())
        if conversation_count > 0:
            tried_categories.add("conversation")

        criteria_met = {
            "first_steps": (activity_count + test_count) >= 1,
            "century_club": xp >= 100,
            "high_scorer": xp >= 500,
            "xp_master": xp >= 1000,
            "chatterbox": conversation_count >= 1,
            "speaker": speaking_count >= 1,
            "bookworm": "reading" in by_category,
            "well_rounded": WELL_ROUNDED_CATEGORIES.issubset(tried_categories),
            "perfectionist": any(
                mastery >= PERFECTIONIST_THRESHOLD and attempts >= MIN_ATTEMPTS_FOR_MASTERY_CHECK
                for mastery, attempts in mastery_by_category.values()
            ),
            "test_taker": test_count >= 5,
        }

        now = datetime.now(timezone.utc)
        for key, met in criteria_met.items():
            if met:
                await self._user_achievements.unlock(user_id, key, now)

        unlocked_docs = await self._user_achievements.list_by_user(user_id)
        unlocked_at_by_key = {doc["achievement_key"]: doc["unlocked_at"] for doc in unlocked_docs}

        return [
            {"definition": definition, "unlocked_at": unlocked_at_by_key.get(definition["key"])}
            for definition in catalog
        ]
