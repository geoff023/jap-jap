from pydantic import BaseModel, Field


class GrammarExplanationRequest(BaseModel):
    concept: str = Field(min_length=1, max_length=200)
    context: str | None = Field(default=None, max_length=500)


class VocabularyExplanationRequest(BaseModel):
    term: str = Field(min_length=1, max_length=200)
    context: str | None = Field(default=None, max_length=500)


class MistakeExplanationRequest(BaseModel):
    category: str = Field(min_length=1, max_length=50)
    concept: str = Field(min_length=1, max_length=200)
    user_answer: str = Field(min_length=1, max_length=200)
    correct_answer: str = Field(min_length=1, max_length=200)


class GrammarExplanation(BaseModel):
    concept: str
    explanation: str
    example_sentence: str
    example_translation: str


class VocabularyExplanation(BaseModel):
    term: str
    meaning: str
    explanation: str
    example_sentence: str
    example_translation: str


class MistakeExplanation(BaseModel):
    concept: str
    explanation: str
    tip: str
