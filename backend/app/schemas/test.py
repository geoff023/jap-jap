from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.profile import JLPTLevel


class TestCategory(str, Enum):
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    MIXED = "mixed"


class QuestionPublic(BaseModel):
    """A question as shown before answering — no correct_answer/explanation."""

    id: str
    prompt: str
    options: list[str]


class TestSummary(BaseModel):
    id: str
    title: str
    category: TestCategory
    level: JLPTLevel
    question_count: int


class TestDetail(BaseModel):
    id: str
    title: str
    category: TestCategory
    level: JLPTLevel
    questions: list[QuestionPublic]


class AnswerSubmission(BaseModel):
    question_id: str
    selected: str


class SubmitAttemptRequest(BaseModel):
    answers: list[AnswerSubmission] = Field(min_length=1)


class AnswerResult(BaseModel):
    question_id: str
    concept: str
    selected: str
    correct: bool
    correct_answer: str
    explanation: str


class TestAttemptSummary(BaseModel):
    id: str
    test_id: str
    test_title: str
    category: TestCategory
    level: JLPTLevel
    score: int
    total: int
    xp_earned: int
    completed_at: datetime


class TestAttemptDetail(TestAttemptSummary):
    answers: list[AnswerResult]


class SubmitAttemptResponse(TestAttemptDetail):
    total_xp: int


def test_to_summary(test: dict[str, Any]) -> TestSummary:
    return TestSummary(
        id=str(test["_id"]),
        title=test["title"],
        category=test["category"],
        level=test["level"],
        question_count=len(test["question_ids"]),
    )


def test_to_detail(test: dict[str, Any], questions: list[dict[str, Any]]) -> TestDetail:
    return TestDetail(
        id=str(test["_id"]),
        title=test["title"],
        category=test["category"],
        level=test["level"],
        questions=[
            QuestionPublic(id=str(q["_id"]), prompt=q["prompt"], options=q["options"])
            for q in questions
        ],
    )


def attempt_to_summary(attempt: dict[str, Any]) -> TestAttemptSummary:
    return TestAttemptSummary(
        id=str(attempt["_id"]),
        test_id=attempt["test_id"],
        test_title=attempt["test_title"],
        category=attempt["category"],
        level=attempt["level"],
        score=attempt["score"],
        total=attempt["total"],
        xp_earned=attempt["xp_earned"],
        completed_at=attempt["completed_at"],
    )


def attempt_to_detail(attempt: dict[str, Any]) -> TestAttemptDetail:
    return TestAttemptDetail(
        **attempt_to_summary(attempt).model_dump(),
        answers=[AnswerResult(**a) for a in attempt["answers"]],
    )


def submit_response_from(attempt: dict[str, Any]) -> SubmitAttemptResponse:
    return SubmitAttemptResponse(
        **attempt_to_detail(attempt).model_dump(),
        total_xp=attempt["total_xp"],
    )
