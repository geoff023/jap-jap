from datetime import datetime, timezone


async def _user_id(client, headers) -> str:
    response = await client.get("/api/users/me", headers=headers)
    return response.json()["id"]


async def _record_skill(user_id: str, category: str, concept: str, correct: bool):
    from app.core.database import get_database
    from app.repositories.skill_repository import LearnerSkillRepository

    await LearnerSkillRepository(get_database()).record_result(
        user_id, category, concept, correct, datetime.now(timezone.utc)
    )


async def _record_test_attempt(user_id: str):
    from app.core.database import get_database
    from app.repositories.test_attempt_repository import TestAttemptRepository

    await TestAttemptRepository(get_database()).record(
        {
            "user_id": user_id,
            "test_id": "fake-test-id",
            "test_title": "Fake Test",
            "category": "vocabulary",
            "level": "N5",
            "answers": [],
            "score": 1,
            "total": 1,
            "xp_earned": 10,
            "completed_at": datetime.now(timezone.utc),
        }
    )


async def test_achievements_requires_authentication(client):
    response = await client.get("/api/achievements")

    assert response.status_code == 401


async def test_achievements_lists_the_full_catalog_all_locked_for_a_new_learner(
    client, onboarded_auth_headers, seed_achievements
):
    response = await client.get("/api/achievements", headers=onboarded_auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 10
    keys = [a["key"] for a in body]
    assert "first_steps" in keys
    assert "test_taker" in keys
    for achievement in body:
        assert achievement["earned"] is False
        assert achievement["unlocked_at"] is None


async def test_first_steps_unlocks_after_one_quiz(
    client, onboarded_auth_headers, seed_content, seed_achievements
):
    vocab_response = await client.get(
        "/api/vocabulary", params={"level": "N5"}, headers=onboarded_auth_headers
    )
    item = vocab_response.json()[0]
    await client.post(
        "/api/activities/quiz/submit",
        json={
            "category": "vocabulary",
            "level": "N5",
            "answers": [{"item_id": item["id"], "selected": item["meaning"]}],
        },
        headers=onboarded_auth_headers,
    )

    response = await client.get("/api/achievements", headers=onboarded_auth_headers)

    body = response.json()
    first_steps = next(a for a in body if a["key"] == "first_steps")
    assert first_steps["earned"] is True
    assert first_steps["unlocked_at"] is not None
    century_club = next(a for a in body if a["key"] == "century_club")
    assert century_club["earned"] is False


async def test_xp_milestones_unlock_at_the_right_thresholds(
    client, onboarded_auth_headers, seed_achievements
):
    from app.core.database import get_database
    from app.repositories.profile_repository import LearnerProfileRepository

    user_id = await _user_id(client, onboarded_auth_headers)
    await LearnerProfileRepository(get_database()).increment_xp(user_id, 100)

    response = await client.get("/api/achievements", headers=onboarded_auth_headers)

    body = response.json()
    assert next(a for a in body if a["key"] == "century_club")["earned"] is True
    assert next(a for a in body if a["key"] == "high_scorer")["earned"] is False
    assert next(a for a in body if a["key"] == "xp_master")["earned"] is False


async def test_chatterbox_unlocks_after_starting_a_conversation(
    client, onboarded_auth_headers, seed_achievements
):
    await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=onboarded_auth_headers,
    )

    response = await client.get("/api/achievements", headers=onboarded_auth_headers)

    body = response.json()
    assert next(a for a in body if a["key"] == "chatterbox")["earned"] is True
    assert next(a for a in body if a["key"] == "well_rounded")["earned"] is False


async def test_well_rounded_requires_every_category(
    client, onboarded_auth_headers, seed_achievements
):
    user_id = await _user_id(client, onboarded_auth_headers)
    for category in ["vocabulary", "grammar", "kanji", "reading", "speaking"]:
        await _record_skill(user_id, category, f"{category}-concept", correct=True)
    await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=onboarded_auth_headers,
    )

    response = await client.get("/api/achievements", headers=onboarded_auth_headers)

    body = response.json()
    assert next(a for a in body if a["key"] == "well_rounded")["earned"] is True
    assert next(a for a in body if a["key"] == "bookworm")["earned"] is True


async def test_perfectionist_requires_high_mastery_and_enough_attempts(
    client, onboarded_auth_headers, seed_achievements
):
    user_id = await _user_id(client, onboarded_auth_headers)
    for _ in range(5):
        await _record_skill(user_id, "vocabulary", "食べる", correct=True)

    response = await client.get("/api/achievements", headers=onboarded_auth_headers)

    body = response.json()
    assert next(a for a in body if a["key"] == "perfectionist")["earned"] is True


async def test_perfectionist_does_not_unlock_with_too_few_attempts(
    client, onboarded_auth_headers, seed_achievements
):
    user_id = await _user_id(client, onboarded_auth_headers)
    for _ in range(2):
        await _record_skill(user_id, "vocabulary", "食べる", correct=True)

    response = await client.get("/api/achievements", headers=onboarded_auth_headers)

    body = response.json()
    assert next(a for a in body if a["key"] == "perfectionist")["earned"] is False


async def test_test_taker_unlocks_after_five_tests(
    client, onboarded_auth_headers, seed_achievements
):
    user_id = await _user_id(client, onboarded_auth_headers)
    for _ in range(5):
        await _record_test_attempt(user_id)

    response = await client.get("/api/achievements", headers=onboarded_auth_headers)

    body = response.json()
    assert next(a for a in body if a["key"] == "test_taker")["earned"] is True


async def test_unlocked_at_stays_stable_across_repeated_requests(
    client, onboarded_auth_headers, seed_achievements
):
    await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=onboarded_auth_headers,
    )

    first = await client.get("/api/achievements", headers=onboarded_auth_headers)
    second = await client.get("/api/achievements", headers=onboarded_auth_headers)

    first_unlocked = next(a for a in first.json() if a["key"] == "chatterbox")["unlocked_at"]
    second_unlocked = next(a for a in second.json() if a["key"] == "chatterbox")["unlocked_at"]
    assert first_unlocked == second_unlocked
