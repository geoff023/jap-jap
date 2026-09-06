from datetime import datetime, timezone
from typing import Any

from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.test_attempt_repository import TestAttemptRepository
from app.repositories.test_repository import TestRepository
from app.schemas.test import AnswerSubmission

XP_PER_CORRECT = 10


class TestNotFoundError(Exception):
    pass


class AttemptNotFoundError(Exception):
    pass


class ProfileRequiredError(Exception):
    """Raised when a learner tries to earn XP before completing onboarding."""


class TestService:
    def __init__(
        self,
        tests: TestRepository,
        questions: QuestionRepository,
        attempts: TestAttemptRepository,
        profiles: LearnerProfileRepository,
    ):
        self._tests = tests
        self._questions = questions
        self._attempts = attempts
        self._profiles = profiles

    async def list_tests(self) -> list[dict[str, Any]]:
        return await self._tests.list_all()

    async def get_test_detail(self, test_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        test = await self._tests.find_by_id(test_id)
        if test is None:
            raise TestNotFoundError(test_id)

        questions = await self._questions.find_by_ids(test["question_ids"])
        questions_by_id = {str(q["_id"]): q for q in questions}
        ordered = [questions_by_id[qid] for qid in test["question_ids"] if qid in questions_by_id]
        return test, ordered

    async def submit_attempt(
        self, user_id: str, test_id: str, answers: list[AnswerSubmission]
    ) -> dict[str, Any]:
        profile = await self._profiles.find_by_user_id(user_id)
        if profile is None:
            raise ProfileRequiredError(user_id)

        test = await self._tests.find_by_id(test_id)
        if test is None:
            raise TestNotFoundError(test_id)

        questions = await self._questions.find_by_ids([a.question_id for a in answers])
        questions_by_id = {str(q["_id"]): q for q in questions}

        results = []
        score = 0
        for answer in answers:
            question = questions_by_id.get(answer.question_id)
            if question is None:
                continue
            is_correct = answer.selected == question["correct_answer"]
            score += int(is_correct)
            results.append(
                {
                    "question_id": answer.question_id,
                    "concept": question["concept"],
                    "selected": answer.selected,
                    "correct": is_correct,
                    "correct_answer": question["correct_answer"],
                    "explanation": question["explanation"],
                }
            )

        total = len(results)
        xp_earned = score * XP_PER_CORRECT

        attempt = await self._attempts.record(
            {
                "user_id": user_id,
                "test_id": test_id,
                "test_title": test["title"],
                "category": test["category"],
                "level": test["level"],
                "answers": results,
                "score": score,
                "total": total,
                "xp_earned": xp_earned,
                "completed_at": datetime.now(timezone.utc),
            }
        )

        updated_profile = await self._profiles.increment_xp(user_id, xp_earned)
        assert updated_profile is not None

        return {**attempt, "total_xp": updated_profile["xp"]}

    async def list_attempts(self, user_id: str) -> list[dict[str, Any]]:
        return await self._attempts.list_by_user(user_id)

    async def get_attempt(self, user_id: str, attempt_id: str) -> dict[str, Any]:
        attempt = await self._attempts.find_by_id(attempt_id)
        if attempt is None or attempt["user_id"] != user_id:
            raise AttemptNotFoundError(attempt_id)
        return attempt
