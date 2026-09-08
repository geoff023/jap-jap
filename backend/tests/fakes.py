from app.ai.base import AIService, AIServiceError
from app.schemas.ai import GrammarExplanation, MistakeExplanation, VocabularyExplanation
from app.schemas.ai_generation import ComprehensionQuestion, GeneratedMiniStory, GeneratedQuestion
from app.schemas.conversation import ConversationReply
from app.schemas.speech import SpeechTranscription
from app.speech.base import SpeechServiceError, SpeechToTextService


class FakeAIService(AIService):
    """Test double standing in for GeminiService — no automated test should
    ever call the real Gemini API. Set should_fail=True to exercise the
    AIServiceError -> 502 path."""

    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.calls: list[tuple] = []

    async def explain_grammar(self, concept: str, context: str | None = None) -> GrammarExplanation:
        self.calls.append(("grammar", concept, context))
        if self.should_fail:
            raise AIServiceError("fake failure")
        return GrammarExplanation(
            concept=concept,
            explanation=f"Explanation for {concept}",
            example_sentence="例文です。",
            example_translation="This is an example sentence.",
        )

    async def explain_vocabulary(
        self, term: str, context: str | None = None
    ) -> VocabularyExplanation:
        self.calls.append(("vocabulary", term, context))
        if self.should_fail:
            raise AIServiceError("fake failure")
        return VocabularyExplanation(
            term=term,
            meaning="a meaning",
            explanation=f"Explanation for {term}",
            example_sentence="例文です。",
            example_translation="This is an example sentence.",
        )

    async def explain_mistake(
        self, category: str, concept: str, user_answer: str, correct_answer: str
    ) -> MistakeExplanation:
        self.calls.append(("mistake", category, concept, user_answer, correct_answer))
        if self.should_fail:
            raise AIServiceError("fake failure")
        return MistakeExplanation(
            concept=concept,
            explanation=f'You answered "{user_answer}" but it should be "{correct_answer}".',
            tip="Remember this next time!",
        )

    async def generate_vocabulary_question(self, level: str) -> GeneratedQuestion:
        self.calls.append(("generate_vocabulary_question", level))
        if self.should_fail:
            raise AIServiceError("fake failure")
        return GeneratedQuestion(
            concept="食べる",
            prompt='What does "食べる" (たべる) mean?',
            options=["to eat", "to drink", "to see", "to go"],
            correct_answer="to eat",
            explanation="食べる means 'to eat'.",
        )

    async def generate_grammar_question(self, level: str) -> GeneratedQuestion:
        self.calls.append(("generate_grammar_question", level))
        if self.should_fail:
            raise AIServiceError("fake failure")
        return GeneratedQuestion(
            concept="particle-de",
            prompt="図書館___勉強します。",
            options=["を", "が", "で", "は"],
            correct_answer="で",
            explanation="で marks the place where an action happens.",
        )

    async def generate_mini_story(self, level: str, topic: str | None = None) -> GeneratedMiniStory:
        self.calls.append(("generate_mini_story", level, topic))
        if self.should_fail:
            raise AIServiceError("fake failure")
        return GeneratedMiniStory(
            title="A Trip to the Store",
            story="今日、店に行きました。りんごを買いました。",
            translation="Today, I went to the store. I bought an apple.",
            vocab_highlights=["店", "りんご", "買う"],
            comprehension_questions=[
                ComprehensionQuestion(
                    prompt="What did the person buy?",
                    options=["an apple", "a book", "a shirt", "a car"],
                    correct_answer="an apple",
                    explanation="The story says they bought an apple (りんご).",
                ),
                ComprehensionQuestion(
                    prompt="Where did the person go?",
                    options=["school", "the store", "the park", "home"],
                    correct_answer="the store",
                    explanation="The story says they went to the store (店).",
                ),
            ],
        )

    async def continue_conversation(
        self,
        character_name: str,
        character_personality: str,
        scenario_title: str,
        scenario_setting: str,
        level: str,
        history: list[dict[str, str]],
        user_message: str,
    ) -> ConversationReply:
        self.calls.append(
            (
                "continue_conversation",
                character_name,
                scenario_title,
                level,
                list(history),
                user_message,
            )
        )
        if self.should_fail:
            raise AIServiceError("fake failure")
        return ConversationReply(
            reply=f"（{character_name}より）はい、かしこまりました。",
            translation=f"(From {character_name}) Yes, understood.",
        )


class FakeSTTService(SpeechToTextService):
    """Test double standing in for GeminiSTTProvider — no automated test
    should ever call the real Gemini API for transcription. Defaults to
    returning a transcript that exactly matches the "n5-greeting" prompt's
    target text; set `.transcript` to something else to exercise the
    incorrect-answer path, or `.should_fail = True` for the 502 path."""

    def __init__(self, should_fail: bool = False, transcript: str = "おはようございます"):
        self.should_fail = should_fail
        self.transcript = transcript
        self.calls: list[tuple] = []

    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> SpeechTranscription:
        self.calls.append(("transcribe", len(audio_bytes), mime_type))
        if self.should_fail:
            raise SpeechServiceError("fake failure")
        return SpeechTranscription(transcript=self.transcript)
