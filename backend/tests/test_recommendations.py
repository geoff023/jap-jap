from datetime import datetime, timezone


async def _record(user_id: str, category: str, concept: str, correct: bool):
    from app.core.database import get_database
    from app.repositories.skill_repository import LearnerSkillRepository

    await LearnerSkillRepository(get_database()).record_result(
        user_id, category, concept, correct, datetime.now(timezone.utc)
    )


async def _user_id(client, headers) -> str:
    response = await client.get("/api/users/me", headers=headers)
    return response.json()["id"]


async def test_recommendations_requires_authentication(client):
    response = await client.get("/api/recommendations")

    assert response.status_code == 401


async def test_recommendations_nudge_every_untried_category_for_a_new_learner(
    client, onboarded_auth_headers
):
    response = await client.get("/api/recommendations", headers=onboarded_auth_headers)

    assert response.status_code == 200
    recs = response.json()["recommendations"]
    categories = [r["category"] for r in recs]
    assert categories == ["vocabulary", "grammar", "kanji", "reading", "speaking", "conversation"]
    for rec in recs:
        assert rec["reason"] == "try_something_new"
        assert rec["mastery"] is None


async def test_recommendations_flag_weak_mastery_ahead_of_untried_nudges(
    client, onboarded_auth_headers
):
    user_id = await _user_id(client, onboarded_auth_headers)
    await _record(user_id, "vocabulary", "食べる", correct=True)
    await _record(user_id, "vocabulary", "食べる", correct=False)
    await _record(user_id, "vocabulary", "食べる", correct=False)

    response = await client.get("/api/recommendations", headers=onboarded_auth_headers)

    recs = response.json()["recommendations"]
    assert recs[0]["category"] == "vocabulary"
    assert recs[0]["reason"] == "weak_mastery"
    assert recs[0]["mastery"] == 1 / 3
    assert "33%" in recs[0]["message"]
    assert recs[0]["action_path"] == "/quiz"
    # The rest are still untried nudges, sorted after the weak entry.
    assert [r["reason"] for r in recs[1:]] == ["try_something_new"] * 5


async def test_recommendations_ignore_a_category_with_too_few_attempts(
    client, onboarded_auth_headers
):
    user_id = await _user_id(client, onboarded_auth_headers)
    await _record(user_id, "vocabulary", "食べる", correct=True)
    await _record(user_id, "vocabulary", "食べる", correct=False)

    response = await client.get("/api/recommendations", headers=onboarded_auth_headers)

    recs = response.json()["recommendations"]
    assert not any(r["category"] == "vocabulary" for r in recs)


async def test_recommendations_treat_conversation_as_tried_once_a_session_exists(
    client, onboarded_auth_headers
):
    await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=onboarded_auth_headers,
    )

    response = await client.get("/api/recommendations", headers=onboarded_auth_headers)

    recs = response.json()["recommendations"]
    assert not any(r["category"] == "conversation" for r in recs)
    assert len(recs) == 5


async def test_recommendations_fall_back_to_a_challenge_when_everything_looks_solid(
    client, onboarded_auth_headers
):
    user_id = await _user_id(client, onboarded_auth_headers)
    for category in ["vocabulary", "grammar", "kanji", "reading", "speaking"]:
        for _ in range(3):
            await _record(user_id, category, f"{category}-concept", correct=True)
    await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=onboarded_auth_headers,
    )

    response = await client.get("/api/recommendations", headers=onboarded_auth_headers)

    recs = response.json()["recommendations"]
    assert len(recs) == 1
    assert recs[0]["category"] is None
    assert recs[0]["reason"] == "challenge"
    assert recs[0]["action_path"] == "/tests"
