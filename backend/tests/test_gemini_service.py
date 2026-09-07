from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.ai.base import AIServiceError
from app.ai.gemini_service import GeminiService
from app.schemas.ai import GrammarExplanation

# These tests exercise GeminiService's own parse/validate pipeline directly,
# with the SDK's network call mocked out — the real Gemini API must never be
# called from an automated test. Constructing genai.Client() itself makes no
# network call (only generate_content does), so it's safe to build a real
# GeminiService instance and just replace its one network-touching method.


def _service_with_mocked_response(monkeypatch, response_text: str) -> GeminiService:
    service = GeminiService(api_key="fake-key-for-unit-test")
    mock_generate_content = AsyncMock(return_value=SimpleNamespace(text=response_text))
    monkeypatch.setattr(service._client.aio.models, "generate_content", mock_generate_content)
    return service


async def test_explain_grammar_parses_and_validates_a_well_formed_response(monkeypatch):
    service = _service_with_mocked_response(
        monkeypatch,
        '{"concept": "particle-ha", "explanation": "Marks the topic.", '
        '"example_sentence": "わたしは学生です。", '
        '"example_translation": "I am a student."}',
    )

    result = await service.explain_grammar("particle-ha")

    assert isinstance(result, GrammarExplanation)
    assert result.concept == "particle-ha"
    assert result.explanation == "Marks the topic."


async def test_explain_grammar_raises_on_malformed_json(monkeypatch):
    service = _service_with_mocked_response(monkeypatch, "this is not json")

    with pytest.raises(AIServiceError):
        await service.explain_grammar("particle-ha")


async def test_explain_grammar_raises_when_required_fields_are_missing(monkeypatch):
    service = _service_with_mocked_response(monkeypatch, '{"concept": "particle-ha"}')

    with pytest.raises(AIServiceError):
        await service.explain_grammar("particle-ha")


async def test_explain_grammar_raises_on_empty_response(monkeypatch):
    service = _service_with_mocked_response(monkeypatch, "")

    with pytest.raises(AIServiceError):
        await service.explain_grammar("particle-ha")


async def test_underlying_sdk_errors_are_wrapped_as_ai_service_error(monkeypatch):
    service = GeminiService(api_key="fake-key-for-unit-test")

    async def _boom(*args, **kwargs):
        raise RuntimeError("network exploded")

    monkeypatch.setattr(service._client.aio.models, "generate_content", _boom)

    with pytest.raises(AIServiceError):
        await service.explain_grammar("particle-ha")


async def test_generate_vocabulary_question_rejects_fewer_than_four_options(monkeypatch):
    service = _service_with_mocked_response(
        monkeypatch,
        '{"concept": "食べる", "prompt": "What does it mean?", '
        '"options": ["to eat", "to drink", "to see"], "correct_answer": "to eat", '
        '"explanation": "It means to eat."}',
    )

    with pytest.raises(AIServiceError):
        await service.generate_vocabulary_question("N5")


async def test_generate_grammar_question_rejects_a_correct_answer_not_in_options(monkeypatch):
    service = _service_with_mocked_response(
        monkeypatch,
        '{"concept": "particle-de", "prompt": "___", '
        '"options": ["を", "が", "に", "は"], "correct_answer": "で", '
        '"explanation": "..."}',
    )

    with pytest.raises(AIServiceError):
        await service.generate_grammar_question("N5")


async def test_generate_mini_story_rejects_duplicate_options_in_a_comprehension_question(
    monkeypatch,
):
    service = _service_with_mocked_response(
        monkeypatch,
        '{"title": "T", "story": "'
        + "今日はいい天気です。" * 2
        + '", "translation": "It is nice weather today, twice.", '
        '"vocab_highlights": ["天気"], "comprehension_questions": [{"prompt": "Q1?", '
        '"options": ["a", "a", "b", "c"], "correct_answer": "a", "explanation": "..."}, '
        '{"prompt": "Q2?", "options": ["a", "b", "c", "d"], "correct_answer": "a", '
        '"explanation": "..."}]}',
    )

    with pytest.raises(AIServiceError):
        await service.generate_mini_story("N5")


async def test_generate_mini_story_parses_a_well_formed_response(monkeypatch):
    service = _service_with_mocked_response(
        monkeypatch,
        '{"title": "T", "story": "'
        + "今日はいい天気です。" * 2
        + '", "translation": "It is nice weather today, twice.", '
        '"vocab_highlights": ["天気"], "comprehension_questions": [{"prompt": "Q1?", '
        '"options": ["a", "b", "c", "d"], "correct_answer": "a", "explanation": "..."}, '
        '{"prompt": "Q2?", "options": ["a", "b", "c", "d"], "correct_answer": "b", '
        '"explanation": "..."}]}',
    )

    result = await service.generate_mini_story("N5")

    assert result.title == "T"
    assert len(result.comprehension_questions) == 2
