from datetime import datetime, timezone
from typing import Any

from app.ai.base import AIService
from app.repositories.ai_interaction_repository import AIInteractionRepository
from app.repositories.mini_story_repository import MiniStoryRepository
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.schemas.ai_generation import ComprehensionAnswer

XP_PER_CORRECT = 10


class ProfileRequiredError(Exception):
    """Raised when a learner tries to earn XP before completing onboarding."""


class StoryNotFoundError(Exception):
    pass


class QuestionNotFoundError(Exception):
    pass


class ContentGenerationService:
    """Orchestrates AI generation -> Pydantic-validated result (already
    guaranteed by AIService) -> storage. Never lets a raw AI response reach
    the database; the AIService return types are already validated
    GeneratedQuestion/GeneratedMiniStory instances by the time they get here."""

    def __init__(
        self,
        ai: AIService,
        questions: QuestionRepository,
        stories: MiniStoryRepository,
        interactions: AIInteractionRepository,
        profiles: LearnerProfileRepository,
        skills: LearnerSkillRepository,
    ):
        self._ai = ai
        self._questions = questions
        self._stories = stories
        self._interactions = interactions
        self._profiles = profiles
        self._skills = skills

    async def generate_vocabulary_question(self, user_id: str, level: str) -> dict[str, Any]:
        generated = await self._ai.generate_vocabulary_question(level)
        doc = await self._questions.create(
            {
                "category": "vocabulary",
                "level": level,
                "concept": generated.concept,
                "difficulty": "easy",
                "prompt": generated.prompt,
                "options": generated.options,
                "correct_answer": generated.correct_answer,
                "explanation": generated.explanation,
                "source": "ai_generated",
                "created_at": datetime.now(timezone.utc),
            }
        )
        await self._interactions.record(
            user_id, "vocabulary_question_generation", generated.concept
        )
        return doc

    async def generate_grammar_question(self, user_id: str, level: str) -> dict[str, Any]:
        generated = await self._ai.generate_grammar_question(level)
        doc = await self._questions.create(
            {
                "category": "grammar",
                "level": level,
                "concept": generated.concept,
                "difficulty": "easy",
                "prompt": generated.prompt,
                "options": generated.options,
                "correct_answer": generated.correct_answer,
                "explanation": generated.explanation,
                "source": "ai_generated",
                "created_at": datetime.now(timezone.utc),
            }
        )
        await self._interactions.record(user_id, "grammar_question_generation", generated.concept)
        return doc

    async def generate_mini_story(
        self, user_id: str, level: str, topic: str | None
    ) -> dict[str, Any]:
        generated = await self._ai.generate_mini_story(level, topic)
        doc = await self._stories.create(
            {
                "title": generated.title,
                "level": level,
                "story": generated.story,
                "translation": generated.translation,
                "vocab_highlights": generated.vocab_highlights,
                "comprehension_questions": [
                    q.model_dump() for q in generated.comprehension_questions
                ],
                "generated_by_user_id": user_id,
                "created_at": datetime.now(timezone.utc),
            }
        )
        await self._interactions.record(user_id, "mini_story_generation", generated.title)
        return doc

    async def submit_comprehension(
        self, user_id: str, story_id: str, answers: list[ComprehensionAnswer]
    ) -> dict[str, Any]:
        profile = await self._profiles.find_by_user_id(user_id)
        if profile is None:
            raise ProfileRequiredError(user_id)

        story = await self._stories.find_by_id(story_id)
        if story is None or story["generated_by_user_id"] != user_id:
            raise StoryNotFoundError(story_id)

        questions = story["comprehension_questions"]
        now = datetime.now(timezone.utc)
        results = []
        score = 0
        for answer in answers:
            if not (0 <= answer.index < len(questions)):
                continue
            question = questions[answer.index]
            is_correct = answer.selected == question["correct_answer"]
            score += int(is_correct)
            results.append(
                {
                    "index": answer.index,
                    "selected": answer.selected,
                    "correct": is_correct,
                    "correct_answer": question["correct_answer"],
                    "explanation": question["explanation"],
                }
            )
            # "reading" has no other data source yet (see docs/PROJECT_STATE.md
            # Phase 5) — comprehension questions are the first real signal
            # for that category in the learner model.
            await self._skills.record_result(user_id, "reading", story["title"], is_correct, now)

        total = len(results)
        xp_earned = score * XP_PER_CORRECT
        updated_profile = await self._profiles.increment_xp(user_id, xp_earned)
        assert updated_profile is not None

        return {
            "score": score,
            "total": total,
            "xp_earned": xp_earned,
            "total_xp": updated_profile["xp"],
            "results": results,
        }

    async def submit_generated_question(
        self, user_id: str, question_id: str, selected: str
    ) -> dict[str, Any]:
        profile = await self._profiles.find_by_user_id(user_id)
        if profile is None:
            raise ProfileRequiredError(user_id)

        question = await self._questions.find_by_id(question_id)
        if question is None:
            raise QuestionNotFoundError(question_id)

        is_correct = selected == question["correct_answer"]
        xp_earned = XP_PER_CORRECT if is_correct else 0

        await self._skills.record_result(
            user_id,
            question["category"],
            question["concept"],
            is_correct,
            datetime.now(timezone.utc),
        )
        updated_profile = await self._profiles.increment_xp(user_id, xp_earned)
        assert updated_profile is not None

        return {
            "correct": is_correct,
            "correct_answer": question["correct_answer"],
            "explanation": question["explanation"],
            "xp_earned": xp_earned,
            "total_xp": updated_profile["xp"],
        }
