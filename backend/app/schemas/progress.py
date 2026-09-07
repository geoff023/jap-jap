from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.profile import JLPTLevel

# The full skill list from the master spec's learner model. Only vocabulary
# and grammar have a data source as of Phase 5 — the rest always report
# has_data=False until a later phase adds kanji/reading/listening/speaking/
# conversation content or activities.
TRACKED_CATEGORIES = [
    "vocabulary",
    "grammar",
    "kanji",
    "reading",
    "listening",
    "speaking",
    "conversation",
]


class CategoryProgress(BaseModel):
    category: str
    mastery: float | None
    concepts_tracked: int
    has_data: bool


class OverallProgress(BaseModel):
    mastery: float | None
    has_data: bool


class JLPTReadiness(BaseModel):
    jlpt_target: JLPTLevel | None
    score: float | None
    has_data: bool


class ProgressResponse(BaseModel):
    overall: OverallProgress
    skills: list[CategoryProgress]
    estimated_jlpt_readiness: JLPTReadiness


class MistakeEntry(BaseModel):
    category: str
    concept: str
    occurrences: int
    mastery: float
    last_seen: datetime


def mistake_to_public(doc: dict[str, Any]) -> MistakeEntry:
    correct = doc.get("correct_count", 0)
    incorrect = doc.get("incorrect_count", 0)
    return MistakeEntry(
        category=doc["category"],
        concept=doc["concept"],
        occurrences=incorrect,
        mastery=correct / (correct + incorrect),
        last_seen=doc["last_seen"],
    )
