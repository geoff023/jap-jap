import json

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.ai.base import AIService, AIServiceError
from app.schemas.ai import GrammarExplanation, MistakeExplanation, VocabularyExplanation
from app.schemas.ai_generation import GeneratedMiniStory, GeneratedQuestion

DEFAULT_MODEL = "gemini-2.0-flash"


class GeminiService(AIService):
    """Gemini-backed implementation of AIService.

    Every method: build a prompt that tells Gemini the exact JSON shape we
    need -> request JSON output -> parse -> validate against our own
    Pydantic schema. We never rely on the SDK's own schema-binding/auto-parse
    feature as the source of truth — our Pydantic model is what actually
    gates whether a response is usable, per docs/AI.md's
    Gemini -> structured output -> Pydantic validation -> ... pipeline.
    """

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def _generate_json(self, prompt: str) -> dict:
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
        except Exception as exc:
            raise AIServiceError("Gemini request failed") from exc

        text = response.text
        if not text:
            raise AIServiceError("Gemini returned an empty response")

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise AIServiceError("Gemini returned a non-JSON response") from exc

    async def explain_grammar(self, concept: str, context: str | None = None) -> GrammarExplanation:
        context_clause = f' The learner encountered it in: "{context}".' if context else ""
        prompt = (
            f"You are a friendly Japanese language tutor. Explain the Japanese grammar "
            f'point "{concept}" to a learner.{context_clause} '
            "Respond with ONLY a JSON object (no markdown, no extra text) with exactly "
            'these keys: "concept" (string), "explanation" (a clear, concise explanation, '
            '2-4 sentences), "example_sentence" (an original Japanese example sentence '
            'using it), "example_translation" (its English translation).'
        )
        data = await self._generate_json(prompt)
        try:
            return GrammarExplanation.model_validate(data)
        except ValidationError as exc:
            raise AIServiceError(
                "Gemini's grammar explanation didn't match the expected format"
            ) from exc

    async def explain_vocabulary(
        self, term: str, context: str | None = None
    ) -> VocabularyExplanation:
        context_clause = f' The learner encountered it in: "{context}".' if context else ""
        prompt = (
            f"You are a friendly Japanese language tutor. Explain the Japanese word or "
            f'phrase "{term}" to a learner.{context_clause} '
            "Respond with ONLY a JSON object (no markdown, no extra text) with exactly "
            'these keys: "term" (string, the word itself), "meaning" (concise English '
            'meaning), "explanation" (2-4 sentences of nuance/usage notes), '
            '"example_sentence" (an original Japanese example sentence using it), '
            '"example_translation" (its English translation).'
        )
        data = await self._generate_json(prompt)
        try:
            return VocabularyExplanation.model_validate(data)
        except ValidationError as exc:
            raise AIServiceError(
                "Gemini's vocabulary explanation didn't match the expected format"
            ) from exc

    async def explain_mistake(
        self, category: str, concept: str, user_answer: str, correct_answer: str
    ) -> MistakeExplanation:
        prompt = (
            f"You are a friendly Japanese language tutor helping a learner understand a "
            f'mistake. Category: {category}. Concept: "{concept}". The learner answered '
            f'"{user_answer}" but the correct answer is "{correct_answer}". '
            "Respond with ONLY a JSON object (no markdown, no extra text) with exactly "
            'these keys: "concept" (string), "explanation" (2-3 sentences on why the '
            'correct answer is right and the learner\'s answer was wrong), "tip" (one '
            "short, memorable tip to avoid this mistake next time)."
        )
        data = await self._generate_json(prompt)
        try:
            return MistakeExplanation.model_validate(data)
        except ValidationError as exc:
            raise AIServiceError(
                "Gemini's mistake explanation didn't match the expected format"
            ) from exc

    async def generate_vocabulary_question(self, level: str) -> GeneratedQuestion:
        prompt = (
            f"You are creating a Japanese vocabulary practice question for a JLPT {level} "
            "learner. Pick one JLPT-appropriate vocabulary word for that level. "
            "Respond with ONLY a JSON object (no markdown, no extra text) with exactly "
            'these keys: "concept" (the Japanese word itself), "prompt" (a question asking '
            'what the word means, including the word and its reading), "options" (an array '
            "of exactly 4 distinct English meanings, one of which is correct), "
            '"correct_answer" (must exactly match one of the 4 options), "explanation" '
            "(1-2 sentences explaining the correct meaning)."
        )
        data = await self._generate_json(prompt)
        try:
            return GeneratedQuestion.model_validate(data)
        except ValidationError as exc:
            raise AIServiceError(
                "Gemini's generated vocabulary question didn't match the expected format"
            ) from exc

    async def generate_grammar_question(self, level: str) -> GeneratedQuestion:
        prompt = (
            f"You are creating a Japanese grammar practice question for a JLPT {level} "
            "learner. Pick one JLPT-appropriate grammar point for that level (e.g. a "
            "particle or verb conjugation). "
            "Respond with ONLY a JSON object (no markdown, no extra text) with exactly "
            'these keys: "concept" (a short name for the grammar point, e.g. '
            '"particle-de"), "prompt" (an original Japanese sentence with a blank, shown '
            'as "___", testing that grammar point), "options" (an array of exactly 4 '
            "distinct single word/short phrase choices to fill the blank, one of which is "
            'correct), "correct_answer" (must exactly match one of the 4 options), '
            '"explanation" (1-2 sentences explaining why it is correct).'
        )
        data = await self._generate_json(prompt)
        try:
            return GeneratedQuestion.model_validate(data)
        except ValidationError as exc:
            raise AIServiceError(
                "Gemini's generated grammar question didn't match the expected format"
            ) from exc

    async def generate_mini_story(self, level: str, topic: str | None = None) -> GeneratedMiniStory:
        topic_clause = f' about "{topic}"' if topic else ""
        prompt = (
            f"You are writing a short original Japanese story{topic_clause} for a JLPT "
            f"{level} learner, plus reading comprehension questions about it. "
            "Respond with ONLY a JSON object (no markdown, no extra text) with exactly "
            'these keys: "title" (a short title), "story" (an original short story in '
            f"Japanese, 3-6 sentences, using vocabulary and grammar appropriate for JLPT "
            f'{level}), "translation" (the English translation of the story), '
            '"vocab_highlights" (an array of 3-8 notable Japanese words/phrases from the '
            'story worth studying), "comprehension_questions" (an array of 2-3 objects, '
            'each with keys "prompt" (a comprehension question in English about the '
            'story), "options" (an array of exactly 4 distinct English answer choices, '
            'one of which is correct), "correct_answer" (must exactly match one of the 4 '
            'options), "explanation" (1 sentence citing what in the story supports the '
            "answer))."
        )
        data = await self._generate_json(prompt)
        try:
            return GeneratedMiniStory.model_validate(data)
        except ValidationError as exc:
            raise AIServiceError(
                "Gemini's generated mini story didn't match the expected format"
            ) from exc
