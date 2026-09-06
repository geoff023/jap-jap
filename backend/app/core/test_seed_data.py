"""Derives Phase 4 Test Engine content (Question documents, grouped into
Test documents) from the Phase 3 seed vocabulary/grammar.

One source of truth for N5 content rather than two independently maintained
datasets. Distractor choice is index-based (not random) so seeded content is
stable and reproducible across app restarts and test runs.
"""

from typing import TYPE_CHECKING

from app.core.seed_data import GRAMMAR_N5, VOCABULARY_N5

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase


def _vocabulary_question(item: dict, index: int, pool: list[dict]) -> dict:
    other_meanings = [v["meaning"] for v in pool if v["meaning"] != item["meaning"]]
    distractors = [
        other_meanings[(index + 1) % len(other_meanings)],
        other_meanings[(index + 2) % len(other_meanings)],
        other_meanings[(index + 3) % len(other_meanings)],
    ]
    options = distractors.copy()
    options.insert(index % 4, item["meaning"])

    return {
        "category": "vocabulary",
        "level": item["level"],
        "concept": item["term"],
        "difficulty": "easy",
        "prompt": f'What does "{item["term"]}" ({item["reading"]}) mean?',
        "options": options,
        "correct_answer": item["meaning"],
        "explanation": f'{item["term"]} ({item["reading"]}) means "{item["meaning"]}".',
    }


def _grammar_question(item: dict, index: int, pool: list[dict]) -> dict:
    other_answers = [g["answer"] for g in pool if g["answer"] != item["answer"]]
    distractors = [
        other_answers[(index + 1) % len(other_answers)],
        other_answers[(index + 2) % len(other_answers)],
        other_answers[(index + 3) % len(other_answers)],
    ]
    options = distractors.copy()
    options.insert(index % 4, item["answer"])

    return {
        "category": "grammar",
        "level": item["level"],
        "concept": item["key"],
        "difficulty": "easy",
        "prompt": item["example_sentence"],
        "options": options,
        "correct_answer": item["answer"],
        "explanation": item["explanation"],
    }


def build_question_documents() -> list[dict]:
    vocabulary_questions = [
        _vocabulary_question(item, i, VOCABULARY_N5) for i, item in enumerate(VOCABULARY_N5)
    ]
    grammar_questions = [
        _grammar_question(item, i, GRAMMAR_N5) for i, item in enumerate(GRAMMAR_N5)
    ]
    return vocabulary_questions + grammar_questions


def build_test_documents(vocabulary_ids: list[str], grammar_ids: list[str]) -> list[dict]:
    return [
        {
            "title": "N5 Vocabulary Test",
            "category": "vocabulary",
            "level": "N5",
            "question_ids": vocabulary_ids,
        },
        {
            "title": "N5 Grammar Test",
            "category": "grammar",
            "level": "N5",
            "question_ids": grammar_ids,
        },
        {
            "title": "N5 Mixed Test",
            "category": "mixed",
            "level": "N5",
            "question_ids": vocabulary_ids + grammar_ids,
        },
    ]


async def seed_test_engine(db: "AsyncIOMotorDatabase") -> None:
    """Seed questions, then group them into tests — idempotent either way.

    Tests reference questions by id, so tests can only be built after
    question ids are known; question ids are always looked up fresh (by
    category) rather than trusted from an insert_many call, so this works
    correctly whether questions were just seeded or already existed.
    """
    from app.repositories.question_repository import QuestionRepository
    from app.repositories.test_repository import TestRepository

    question_repo = QuestionRepository(db)
    test_repo = TestRepository(db)

    await question_repo.seed_if_empty(build_question_documents())

    if await test_repo.count() > 0:
        return

    vocabulary_ids = [str(q["_id"]) for q in await question_repo.list_by_category("vocabulary")]
    grammar_ids = [str(q["_id"]) for q in await question_repo.list_by_category("grammar")]
    await test_repo.seed_if_empty(build_test_documents(vocabulary_ids, grammar_ids))
