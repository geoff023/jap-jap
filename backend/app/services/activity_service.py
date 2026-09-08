import random
from datetime import datetime, timezone
from typing import Any

from app.repositories.activity_repository import ActivityRepository
from app.repositories.grammar_repository import GrammarRepository
from app.repositories.kanji_repository import KanjiRepository
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.review_schedule_repository import (
    UNSEEN_SORT_KEY,
    ReviewScheduleRepository,
)
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


# (prompt_field, answer_field) per category — vocabulary and kanji quizzes
# are "multiple choice" (term/character -> meaning), grammar quizzes are
# "sentence completion" (fill the blank in example_sentence with the right
# word).
_QUIZ_FIELDS = {
    ActivityCategory.VOCABULARY: ("term", "meaning"),
    ActivityCategory.GRAMMAR: ("example_sentence", "answer"),
    ActivityCategory.KANJI: ("character", "meaning"),
}

_ACTIVITY_TYPE_FOR_QUIZ = {
    ActivityCategory.VOCABULARY: "multiple_choice",
    ActivityCategory.GRAMMAR: "sentence_completion",
    ActivityCategory.KANJI: "multiple_choice",
}

# The field that identifies *what concept* an item tests — same field
# test_seed_data.py uses to derive Question.concept, so a vocabulary word or
# grammar point is tracked as the same skill whether it was practiced via a
# Phase 3 quiz/flashcard or a Phase 4 test.
_CONCEPT_FIELDS = {
    ActivityCategory.VOCABULARY: "term",
    ActivityCategory.GRAMMAR: "key",
    ActivityCategory.KANJI: "character",
}


class ActivityService:
    def __init__(
        self,
        vocabulary: VocabularyRepository,
        grammar: GrammarRepository,
        kanji: KanjiRepository,
        activities: ActivityRepository,
        profiles: LearnerProfileRepository,
        skills: LearnerSkillRepository,
        review_schedule: ReviewScheduleRepository,
    ):
        self._vocabulary = vocabulary
        self._grammar = grammar
        self._kanji = kanji
        self._activities = activities
        self._profiles = profiles
        self._skills = skills
        self._review_schedule = review_schedule
        self._content_repos = {
            ActivityCategory.VOCABULARY: vocabulary,
            ActivityCategory.GRAMMAR: grammar,
            ActivityCategory.KANJI: kanji,
        }

    def _content_repo(
        self, category: ActivityCategory
    ) -> VocabularyRepository | GrammarRepository | KanjiRepository:
        return self._content_repos[category]

    async def _rank_by_due_date(
        self, user_id: str, category: ActivityCategory, pool: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Most-overdue (or never-reviewed) concepts first, so quizzes and
        flashcards surface what a learner needs to revisit instead of
        re-serving whatever they already answered correctly moments ago.
        Random tie-break among equally-due items keeps repeat generations
        from feeling mechanically identical."""
        concept_field = _CONCEPT_FIELDS[category]
        due_dates = await self._review_schedule.due_dates_by_concept(user_id, category.value)

        shuffled = list(pool)
        random.shuffle(shuffled)
        return sorted(
            shuffled, key=lambda item: due_dates.get(item[concept_field], UNSEEN_SORT_KEY)
        )

    async def generate_quiz(
        self, user_id: str, category: ActivityCategory, level: JLPTLevel, size: int
    ) -> list[QuizQuestion]:
        pool = await self._content_repo(category).list_by_level(level.value)
        if len(pool) < QUIZ_OPTION_COUNT:
            raise NotEnoughContentError(f"Not enough {category.value} content for {level.value}")

        prompt_field, answer_field = _QUIZ_FIELDS[category]
        ranked = await self._rank_by_due_date(user_id, category, pool)
        chosen = ranked[: min(size, len(ranked))]

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
            await self._review_schedule.record_review(
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
            await self._review_schedule.record_review(
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

    async def get_flashcard_deck(
        self, user_id: str, category: ActivityCategory, level: JLPTLevel
    ) -> list[dict[str, Any]]:
        """Every item in the level, reordered so due-for-review and
        never-seen concepts come first — unlike generate_quiz, nothing is
        dropped, since flashcard mode is meant for reviewing the whole
        deck, just in a smarter order."""
        pool = await self._content_repo(category).list_by_level(level.value)
        return await self._rank_by_due_date(user_id, category, pool)
