from abc import ABC, abstractmethod

from app.schemas.ai import GrammarExplanation, MistakeExplanation, VocabularyExplanation
from app.schemas.ai_generation import GeneratedMiniStory, GeneratedQuestion


class AIServiceError(Exception):
    """Raised when the AI provider fails or returns something that doesn't
    validate against our expected structured response — callers must never
    let a raw provider error or unvalidated payload reach the database or
    the client."""


class AIService(ABC):
    """Application code depends on this interface, never on a specific
    provider's SDK directly — see docs/AI.md. `GeminiService` is the only
    implementation today, but nothing outside `app/ai/` should know that."""

    @abstractmethod
    async def explain_grammar(self, concept: str, context: str | None = None) -> GrammarExplanation:
        """Explain a grammar point (e.g. a particle, a verb conjugation)."""

    @abstractmethod
    async def explain_vocabulary(
        self, term: str, context: str | None = None
    ) -> VocabularyExplanation:
        """Explain a vocabulary word/phrase."""

    @abstractmethod
    async def explain_mistake(
        self, category: str, concept: str, user_answer: str, correct_answer: str
    ) -> MistakeExplanation:
        """Explain why a specific answer was wrong and how to remember the
        correct one — used for mistake review, not scoring (scoring is
        always deterministic backend logic, never AI)."""

    @abstractmethod
    async def generate_vocabulary_question(self, level: str) -> GeneratedQuestion:
        """Generate a supplementary multiple-choice vocabulary question at
        the given JLPT level — distinct from the hand-authored seed content."""

    @abstractmethod
    async def generate_grammar_question(self, level: str) -> GeneratedQuestion:
        """Generate a supplementary sentence-completion grammar question."""

    @abstractmethod
    async def generate_mini_story(self, level: str, topic: str | None = None) -> GeneratedMiniStory:
        """Generate a short story with reading comprehension questions, both
        in one call — cheaper than generating the story and its questions
        separately, and keeps the questions grounded in the same story."""
