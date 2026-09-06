from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.profile import JLPTLevel


class ActivityCategory(str, Enum):
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"


class QuizQuestion(BaseModel):
    item_id: str
    prompt: str
    options: list[str]


class QuizResponse(BaseModel):
    category: ActivityCategory
    level: JLPTLevel
    questions: list[QuizQuestion]


class QuizAnswer(BaseModel):
    item_id: str
    selected: str


class QuizSubmitRequest(BaseModel):
    category: ActivityCategory
    level: JLPTLevel
    answers: list[QuizAnswer] = Field(min_length=1)


class QuizResultItem(BaseModel):
    item_id: str
    correct: bool
    correct_answer: str


class QuizSubmitResponse(BaseModel):
    correct_count: int
    total: int
    xp_earned: int
    total_xp: int
    results: list[QuizResultItem]


class FlashcardReview(BaseModel):
    item_id: str
    known: bool


class FlashcardCompleteRequest(BaseModel):
    category: ActivityCategory
    level: JLPTLevel
    reviewed: list[FlashcardReview] = Field(min_length=1)


class FlashcardCompleteResponse(BaseModel):
    known_count: int
    total: int
    xp_earned: int
    total_xp: int
