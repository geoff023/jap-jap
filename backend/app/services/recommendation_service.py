from typing import Any

from app.repositories.conversation_repository import ConversationSessionRepository
from app.repositories.skill_repository import LearnerSkillRepository

# Below this many combined attempts for a category, a mastery figure is too
# noisy to act on — same "not enough data yet" caution used elsewhere in the
# learner model (see MIN_ATTEMPTS_FOR_READINESS in learner_model_service.py).
MIN_ATTEMPTS_FOR_WEAKNESS = 3
WEAK_MASTERY_THRESHOLD = 0.7

# Only categories with an actual practice route to recommend — kanji and
# listening have no implemented content yet (see docs/PROJECT_STATE.md), so
# there is nothing useful to link a recommendation to.
CATEGORY_ACTIONS: dict[str, dict[str, str]] = {
    "vocabulary": {
        "untried_message": "Try a vocabulary quiz to start building your profile.",
        "weak_message": (
            "Your vocabulary mastery is {pct}% — review some flashcards or try another quiz."
        ),
        "action_label": "Practice vocabulary",
        "action_path": "/quiz",
    },
    "grammar": {
        "untried_message": "Try a grammar quiz to pick up a few new patterns.",
        "weak_message": "Your grammar mastery is {pct}% — a bit of review could help.",
        "action_label": "Practice grammar",
        "action_path": "/quiz",
    },
    "reading": {
        "untried_message": "Read a mini story and test your comprehension.",
        "weak_message": "Your reading comprehension is at {pct}% — try another mini story.",
        "action_label": "Read a mini story",
        "action_path": "/mini-stories",
    },
    "speaking": {
        "untried_message": "Give Speaking Practice a try — record yourself and get feedback.",
        "weak_message": "Your pronunciation match rate is {pct}% — practice a few more phrases.",
        "action_label": "Practice speaking",
        "action_path": "/speaking",
    },
    "conversation": {
        "untried_message": "Start a conversation with an AI character to practice real dialogue.",
        "action_label": "Start a conversation",
        "action_path": "/conversation",
    },
}

# Conversation deliberately never writes to learner_skills (see AI.md), so
# "has this been tried" for it can't come from mastery data the way it can
# for every other category — it's answered by checking for a session
# directly.
CATEGORIES_SCORED_BY_MASTERY = ["vocabulary", "grammar", "reading", "speaking"]


class RecommendationService:
    def __init__(
        self, skills: LearnerSkillRepository, conversations: ConversationSessionRepository
    ):
        self._skills = skills
        self._conversations = conversations

    async def get_recommendations(self, user_id: str) -> list[dict[str, Any]]:
        skill_docs = await self._skills.list_by_user(user_id)
        by_category: dict[str, list[dict[str, Any]]] = {}
        for doc in skill_docs:
            by_category.setdefault(doc["category"], []).append(doc)

        recommendations: list[dict[str, Any]] = []

        for category in CATEGORIES_SCORED_BY_MASTERY:
            docs = by_category.get(category, [])
            correct = sum(d.get("correct_count", 0) for d in docs)
            incorrect = sum(d.get("incorrect_count", 0) for d in docs)
            attempts = correct + incorrect
            actions = CATEGORY_ACTIONS[category]

            if attempts == 0:
                recommendations.append(
                    {
                        "category": category,
                        "reason": "try_something_new",
                        "message": actions["untried_message"],
                        "mastery": None,
                        "action_label": actions["action_label"],
                        "action_path": actions["action_path"],
                    }
                )
                continue

            mastery = correct / attempts
            if attempts >= MIN_ATTEMPTS_FOR_WEAKNESS and mastery < WEAK_MASTERY_THRESHOLD:
                recommendations.append(
                    {
                        "category": category,
                        "reason": "weak_mastery",
                        "message": actions["weak_message"].format(pct=round(mastery * 100)),
                        "mastery": mastery,
                        "action_label": actions["action_label"],
                        "action_path": actions["action_path"],
                    }
                )

        conversation_sessions = await self._conversations.list_by_user(user_id, limit=1)
        if not conversation_sessions:
            actions = CATEGORY_ACTIONS["conversation"]
            recommendations.append(
                {
                    "category": "conversation",
                    "reason": "try_something_new",
                    "message": actions["untried_message"],
                    "mastery": None,
                    "action_label": actions["action_label"],
                    "action_path": actions["action_path"],
                }
            )

        # Weakest mastery first, then untried nudges (mastery=None sorts
        # last since there's no number to rank untried categories by —
        # they're all equally "worth a look").
        recommendations.sort(key=lambda r: r["mastery"] if r["mastery"] is not None else 1.0)

        if not recommendations:
            recommendations.append(
                {
                    "category": None,
                    "reason": "challenge",
                    "message": (
                        "Great work! Your practice categories all look solid — try a full "
                        "test to challenge yourself."
                    ),
                    "mastery": None,
                    "action_label": "Take a test",
                    "action_path": "/tests",
                }
            )

        return recommendations
