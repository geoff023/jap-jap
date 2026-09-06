from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class LearningGoal(str, Enum):
    ANIME_MANGA = "anime_manga"
    TRAVEL = "travel"
    CONVERSATION = "conversation"
    JLPT = "jlpt"
    UNIVERSITY = "university"
    WORK = "work"
    CULTURE = "culture"
    FUN = "fun"


class ExperienceLevel(str, Enum):
    COMPLETE_BEGINNER = "complete_beginner"
    KNOWS_SOME_WORDS = "knows_some_words"
    KNOWS_HIRAGANA = "knows_hiragana"
    KNOWS_HIRAGANA_KATAKANA = "knows_hiragana_katakana"
    BASIC_GRAMMAR = "basic_grammar"
    PREVIOUSLY_STUDIED = "previously_studied"


class PracticeLevel(str, Enum):
    """A level the learner can freely practise at. No lock, no forced order."""

    N5 = "N5"
    N4 = "N4"
    N3 = "N3"
    N2 = "N2"
    N1 = "N1"
    CONVERSATION = "conversation"


class JLPTLevel(str, Enum):
    N5 = "N5"
    N4 = "N4"
    N3 = "N3"
    N2 = "N2"
    N1 = "N1"


class OnboardingRequest(BaseModel):
    goals: list[LearningGoal] = Field(min_length=1)
    experience: ExperienceLevel
    preferred_level: PracticeLevel
    jlpt_target: JLPTLevel | None = None


class ProfileUpdateRequest(BaseModel):
    """All fields optional: only fields present in the request body are changed.

    Use `model_dump(exclude_unset=True)` on this, not `.dict()`, so an
    omitted field is left untouched while an explicit `null` (e.g.
    `jlpt_target: null`) still clears it.
    """

    goals: list[LearningGoal] | None = Field(default=None, min_length=1)
    experience: ExperienceLevel | None = None
    preferred_level: PracticeLevel | None = None
    jlpt_target: JLPTLevel | None = None


class LearnerProfilePublic(BaseModel):
    user_id: str
    goals: list[LearningGoal]
    experience: ExperienceLevel
    preferred_level: PracticeLevel
    estimated_level: PracticeLevel | None = None
    jlpt_target: JLPTLevel | None = None
    onboarding_completed: bool
    xp: int = 0
    created_at: datetime
    updated_at: datetime


def profile_to_public(profile: dict) -> LearnerProfilePublic:
    return LearnerProfilePublic(
        user_id=profile["user_id"],
        goals=profile["goals"],
        experience=profile["experience"],
        preferred_level=profile["preferred_level"],
        estimated_level=profile.get("estimated_level"),
        jlpt_target=profile.get("jlpt_target"),
        onboarding_completed=profile["onboarding_completed"],
        xp=profile.get("xp", 0),
        created_at=profile["created_at"],
        updated_at=profile["updated_at"],
    )
