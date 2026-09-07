import random
from datetime import datetime, timezone
from typing import Any

from app.repositories.activity_repository import ActivityRepository
from app.repositories.grammar_repository import GrammarRepository
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.schemas.activity import (
    ActivityCategory,
    FlashcardReview,
    QuizAnswer,
    QuizQuestion,
)
from app.schemas.profile import JLPTLevel

QUIZ_OPTION_COUNT = 4
QUIZ_XP_PER_CORRECT = 10
FLASHCARD_XP_PER_KNOWN = 5


class NotEnoughContentError(Exception):
    """Raised when a level/category doesn't have enough seeded items to
    build a multiple-choice question (1 correct + at least 3 distractors)."""


class ProfileRequiredError(Exception):
    """Raised when a learner tries to earn XP before completing onboarding."""


# (prompt_field, answer_field) per category — vocabulary quizzes are
# "multiple choice" (term -> meaning), grammar quizzes are "sentence
# completion" (fill the blank in example_sentence with the right word).
_QUIZ_FIELDS = {
    ActivityCategory.VOCABULARY: ("term", "meaning"),
    ActivityCategory.GRAMMAR: ("example_sentence", "answer"),
}

_ACTIVITY_TYPE_FOR_QUIZ = {
    ActivityCategory.VOCABULARY: "multiple_choice",
    ActivityCategory.GRAMMAR: "sentence_completion",
}

# The field that identifies *what concept* an item tests — same field
# test_seed_data.py uses to derive Question.concept, so a vocabulary word or
# grammar point is tracked as the same skill whether it was practiced via a
# Phase 3 quiz/flashcard or a Phase 4 test.
_CONCEPT_FIELDS = {
    ActivityCategory.VOCABULARY: "term",
    ActivityCategory.GRAMMAR: "key",
}


class ActivityService:
    def __init__(
        self,
        vocabulary: VocabularyRepository,
        grammar: GrammarRepository,
        activities: ActivityRepository,
        profiles: LearnerProfileRepository,
        skills: LearnerSkillRepository,
    ):
        self._vocabulary = vocabulary
        self._grammar = grammar
        self._activities = activities
        self._profiles = profiles
        self._skills = skills

    def _content_repo(self, category: ActivityCategory) -> VocabularyRepository | GrammarRepository:
        return self._vocabulary if category == ActivityCategory.VOCABULARY else self._grammar

    async def generate_quiz(
        self, category: ActivityCategory, level: JLPTLevel, size: int
    ) -> list[QuizQuestion]:
        pool = await self._content_repo(category).list_by_level(level.value)
        if len(pool) < QUIZ_OPTION_COUNT:
            raise NotEnoughContentError(f"Not enough {category.value} content for {level.value}")

        prompt_field, answer_field = _QUIZ_FIELDS[category]
        chosen = random.sample(pool, k=min(size, len(pool)))

        questions = []
        for item in chosen:
            correct_answer = item[answer_field]
            distractor_pool = [p[answer_field] for p in pool if p["_id"] != item["_id"]]
            distractors = random.sample(
                distractor_pool, k=min(QUIZ_OPTION_COUNT - 1, len(distractor_pool))
            )
            options = [*distractors, correct_answer]
            random.shuffle(options)
            questions.append(
                QuizQuestion(item_id=str(item["_id"]), prompt=item[prompt_field], options=options)
            )
        return questions

    async def submit_quiz(
        self,
        user_id: str,
        category: ActivityCategory,
        level: JLPTLevel,
        answers: list[QuizAnswer],
    ) -> dict[str, Any]:
        profile = await self._profiles.find_by_user_id(user_id)
        if profile is None:
            raise ProfileRequiredError(user_id)

        _, answer_field = _QUIZ_FIELDS[category]
        concept_field = _CONCEPT_FIELDS[category]
        items = await self._content_repo(category).find_by_ids([a.item_id for a in answers])
        items_by_id = {str(item["_id"]): item for item in items}

        now = datetime.now(timezone.utc)
        results = []
        correct_count = 0
        for answer in answers:
            item = items_by_id.get(answer.item_id)
            if item is None:
                continue
            correct_answer = item[answer_field]
            is_correct = answer.selected == correct_answer
            correct_count += int(is_correct)
            results.append(
                {
                    "item_id": answer.item_id,
                    "correct": is_correct,
                    "correct_answer": correct_answer,
                }
            )
            await self._skills.record_result(
                user_id, category.value, item[concept_field], is_correct, now
            )

        total = len(results)
        xp_earned = correct_count * QUIZ_XP_PER_CORRECT
        await self._activities.record(
            {
                "user_id": user_id,
                "category": category.value,
                "activity_type": _ACTIVITY_TYPE_FOR_QUIZ[category],
                "level": level.value,
                "correct_count": correct_count,
                "total": total,
                "xp_earned": xp_earned,
                "created_at": now,
            }
        )
        updated_profile = await self._profiles.increment_xp(user_id, xp_earned)
        assert updated_profile is not None

        return {
            "correct_count": correct_count,
            "total": total,
            "xp_earned": xp_earned,
            "total_xp": updated_profile["xp"],
            "results": results,
        }

    async def complete_flashcards(
        self,
        user_id: str,
        category: ActivityCategory,
        level: JLPTLevel,
        reviewed: list[FlashcardReview],
    ) -> dict[str, Any]:
        profile = await self._profiles.find_by_user_id(user_id)
        if profile is None:
            raise ProfileRequiredError(user_id)

        concept_field = _CONCEPT_FIELDS[category]
        items = await self._content_repo(category).find_by_ids([r.item_id for r in reviewed])
        items_by_id = {str(item["_id"]): item for item in items}

        now = datetime.now(timezone.utc)
        known_count = 0
        for review in reviewed:
            known_count += int(review.known)
            item = items_by_id.get(review.item_id)
            if item is None:
                continue
            # Self-assessed, not server-verified — pooled into the same
            # skill signal as quiz/test answers anyway for MVP simplicity;
            # see docs/PROJECT_STATE.md for why that's an acceptable
            # simplification rather than a fabrication.
            await self._skills.record_result(
                user_id, category.value, item[concept_field], review.known, now
            )

        total = len(reviewed)
        xp_earned = known_count * FLASHCARD_XP_PER_KNOWN

        await self._activities.record(
            {
                "user_id": user_id,
                "category": category.value,
                "activity_type": "flashcards",
                "level": level.value,
                "known_count": known_count,
                "total": total,
                "xp_earned": xp_earned,
                "created_at": now,
            }
        )
        updated_profile = await self._profiles.increment_xp(user_id, xp_earned)
        assert updated_profile is not None

        return {
            "known_count": known_count,
            "total": total,
            "xp_earned": xp_earned,
            "total_xp": updated_profile["xp"],
        }
