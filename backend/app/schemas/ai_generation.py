from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.schemas.profile import JLPTLevel

REQUIRED_OPTION_COUNT = 4


class GenerateQuestionRequest(BaseModel):
    level: JLPTLevel


class GenerateMiniStoryRequest(BaseModel):
    level: JLPTLevel
    topic: str | None = Field(default=None, max_length=100)


def _validate_multiple_choice(options: list[str], correct_answer: str) -> None:
    """Business validation beyond Pydantic's type/shape checks — a
    generated question is only usable content if the options are actually a
    well-formed multiple-choice set. Gemini's output must never reach the
    database without this, per docs/AI.md's validation pipeline."""
    if len(options) != REQUIRED_OPTION_COUNT:
        raise ValueError(f"options must contain exactly {REQUIRED_OPTION_COUNT} choices")
    if len(set(options)) != REQUIRED_OPTION_COUNT:
        raise ValueError("options must be unique")
    if correct_answer not in options:
        raise ValueError("correct_answer must be one of options")


class GeneratedQuestion(BaseModel):
    """Gemini's structured output for a vocabulary/grammar question,
    already validated (see model_validator below) by the time application
    code sees an instance of this class."""

    concept: str = Field(min_length=1, max_length=200)
    prompt: str = Field(min_length=1, max_length=500)
    options: list[str]
    correct_answer: str
    explanation: str = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def _validate_options(self) -> "GeneratedQuestion":
        _validate_multiple_choice(self.options, self.correct_answer)
        return self


class ComprehensionQuestion(BaseModel):
    prompt: str = Field(min_length=1, max_length=500)
    options: list[str]
    correct_answer: str
    explanation: str = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def _validate_options(self) -> "ComprehensionQuestion":
        _validate_multiple_choice(self.options, self.correct_answer)
        return self


class GeneratedMiniStory(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    story: str = Field(min_length=20, max_length=2000)
    translation: str = Field(min_length=10, max_length=2000)
    vocab_highlights: list[str] = Field(min_length=1, max_length=15)
    comprehension_questions: list[ComprehensionQuestion] = Field(min_length=2, max_length=5)


class GeneratedQuestionPublic(BaseModel):
    """What the client sees right after generation — no correct_answer, same
    non-cheating contract as the Phase 3/4 quiz and test endpoints."""

    id: str
    category: str
    level: JLPTLevel
    concept: str
    prompt: str
    options: list[str]


class ComprehensionQuestionPublic(BaseModel):
    index: int
    prompt: str
    options: list[str]


class MiniStoryPublic(BaseModel):
    id: str
    title: str
    level: JLPTLevel
    story: str
    translation: str
    vocab_highlights: list[str]
    comprehension_questions: list[ComprehensionQuestionPublic]


class ComprehensionAnswer(BaseModel):
    index: int
    selected: str


class SubmitComprehensionRequest(BaseModel):
    answers: list[ComprehensionAnswer] = Field(min_length=1)


class ComprehensionAnswerResult(BaseModel):
    index: int
    selected: str
    correct: bool
    correct_answer: str
    explanation: str


class SubmitComprehensionResponse(BaseModel):
    score: int
    total: int
    xp_earned: int
    total_xp: int
    results: list[ComprehensionAnswerResult]


class SubmitGeneratedQuestionRequest(BaseModel):
    selected: str = Field(min_length=1, max_length=200)


class SubmitGeneratedQuestionResponse(BaseModel):
    correct: bool
    correct_answer: str
    explanation: str
    xp_earned: int
    total_xp: int


def question_to_public(doc: dict[str, Any]) -> GeneratedQuestionPublic:
    return GeneratedQuestionPublic(
        id=str(doc["_id"]),
        category=doc["category"],
        level=doc["level"],
        concept=doc["concept"],
        prompt=doc["prompt"],
        options=doc["options"],
    )


def mini_story_to_public(doc: dict[str, Any]) -> MiniStoryPublic:
    return MiniStoryPublic(
        id=str(doc["_id"]),
        title=doc["title"],
        level=doc["level"],
        story=doc["story"],
        translation=doc["translation"],
        vocab_highlights=doc["vocab_highlights"],
        comprehension_questions=[
            ComprehensionQuestionPublic(index=i, prompt=q["prompt"], options=q["options"])
            for i, q in enumerate(doc["comprehension_questions"])
        ],
    )
