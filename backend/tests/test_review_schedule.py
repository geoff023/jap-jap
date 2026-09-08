from datetime import datetime, timezone

from app.repositories.review_schedule_repository import ReviewScheduleRepository


async def _get_doc(user_id: str, category: str, concept: str) -> dict:
    from app.core.database import get_database

    db = get_database()
    doc = await db["review_schedule"].find_one(
        {"user_id": user_id, "category": category, "concept": concept}
    )
    assert doc is not None
    return doc


async def test_first_correct_review_sets_a_one_day_interval():
    from app.core.database import get_database

    repo = ReviewScheduleRepository(get_database())
    now = datetime.now(timezone.utc)

    await repo.record_review("user-1", "vocabulary", "食べる", True, now)

    doc = await _get_doc("user-1", "vocabulary", "食べる")
    assert doc["repetitions"] == 1
    assert doc["interval_days"] == 1
    assert doc["ease_factor"] > 2.5


async def test_second_correct_review_sets_a_six_day_interval():
    from app.core.database import get_database

    repo = ReviewScheduleRepository(get_database())
    now = datetime.now(timezone.utc)

    await repo.record_review("user-2", "vocabulary", "食べる", True, now)
    await repo.record_review("user-2", "vocabulary", "食べる", True, now)

    doc = await _get_doc("user-2", "vocabulary", "食べる")
    assert doc["repetitions"] == 2
    assert doc["interval_days"] == 6


async def test_third_correct_review_grows_the_interval_by_the_ease_factor():
    from app.core.database import get_database

    repo = ReviewScheduleRepository(get_database())
    now = datetime.now(timezone.utc)

    await repo.record_review("user-3", "vocabulary", "食べる", True, now)
    await repo.record_review("user-3", "vocabulary", "食べる", True, now)
    await repo.record_review("user-3", "vocabulary", "食べる", True, now)

    doc = await _get_doc("user-3", "vocabulary", "食べる")
    assert doc["repetitions"] == 3
    assert doc["interval_days"] == round(6 * doc["ease_factor"])


async def test_an_incorrect_review_resets_repetitions_and_shortens_the_interval():
    from app.core.database import get_database

    repo = ReviewScheduleRepository(get_database())
    now = datetime.now(timezone.utc)

    await repo.record_review("user-4", "vocabulary", "食べる", True, now)
    await repo.record_review("user-4", "vocabulary", "食べる", True, now)
    ease_before_failure = (await _get_doc("user-4", "vocabulary", "食べる"))["ease_factor"]

    await repo.record_review("user-4", "vocabulary", "食べる", False, now)

    doc = await _get_doc("user-4", "vocabulary", "食べる")
    assert doc["repetitions"] == 0
    assert doc["interval_days"] == 1
    assert doc["ease_factor"] < ease_before_failure


async def test_ease_factor_never_drops_below_the_floor():
    from app.core.database import get_database

    repo = ReviewScheduleRepository(get_database())
    now = datetime.now(timezone.utc)

    for _ in range(20):
        await repo.record_review("user-5", "vocabulary", "食べる", False, now)

    doc = await _get_doc("user-5", "vocabulary", "食べる")
    assert doc["ease_factor"] >= 1.3


async def test_due_dates_by_concept_omits_never_reviewed_concepts():
    from app.core.database import get_database

    repo = ReviewScheduleRepository(get_database())
    now = datetime.now(timezone.utc)
    await repo.record_review("user-6", "vocabulary", "食べる", True, now)

    due_dates = await repo.due_dates_by_concept("user-6", "vocabulary")

    assert "食べる" in due_dates
    assert "飲む" not in due_dates
