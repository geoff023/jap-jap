async def test_generate_vocabulary_question_requires_authentication(client, fake_ai_service):
    response = await client.post("/api/ai/generate/vocabulary-question", json={"level": "N5"})

    assert response.status_code == 401


async def test_generate_vocabulary_question_returns_and_stores_a_question(
    client, auth_headers, fake_ai_service
):
    response = await client.post(
        "/api/ai/generate/vocabulary-question", json={"level": "N5"}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "vocabulary"
    assert body["level"] == "N5"
    assert body["concept"] == "食べる"
    assert len(body["options"]) == 4
    assert "correct_answer" not in body

    # Stored for reuse (e.g. by a future test/quiz), tagged as AI-generated.
    from app.core.database import get_database

    db = get_database()
    # Filter by source, not just concept: the Phase 4 seed data already has
    # a "食べる" question of its own, so concept alone is ambiguous here.
    stored = await db["questions"].find_one({"concept": "食べる", "source": "ai_generated"})
    assert stored is not None
    assert stored["source"] == "ai_generated"
    assert stored["correct_answer"] == "to eat"


async def test_generate_grammar_question_returns_and_stores_a_question(
    client, auth_headers, fake_ai_service
):
    response = await client.post(
        "/api/ai/generate/grammar-question", json={"level": "N5"}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "grammar"
    assert body["concept"] == "particle-de"
    assert "correct_answer" not in body


async def test_generate_question_returns_502_when_ai_fails(client, auth_headers, fake_ai_service):
    fake_ai_service.should_fail = True

    response = await client.post(
        "/api/ai/generate/vocabulary-question", json={"level": "N5"}, headers=auth_headers
    )

    assert response.status_code == 502


async def test_generate_question_returns_503_without_a_configured_api_key(client, auth_headers):
    from app.core.config import Settings, get_settings
    from app.main import app

    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None, gemini_api_key=None)
    try:
        response = await client.post(
            "/api/ai/generate/vocabulary-question", json={"level": "N5"}, headers=auth_headers
        )
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 503


async def test_generate_mini_story_returns_a_story_without_correct_answers(
    client, auth_headers, fake_ai_service
):
    response = await client.post(
        "/api/ai/generate/mini-story", json={"level": "N5"}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "A Trip to the Store"
    assert body["level"] == "N5"
    assert len(body["comprehension_questions"]) == 2
    for question in body["comprehension_questions"]:
        assert set(question.keys()) == {"index", "prompt", "options"}
        assert len(question["options"]) == 4


async def test_submit_comprehension_requires_onboarding(client, auth_headers, fake_ai_service):
    generate_response = await client.post(
        "/api/ai/generate/mini-story", json={"level": "N5"}, headers=auth_headers
    )
    story_id = generate_response.json()["id"]

    response = await client.post(
        f"/api/ai/mini-stories/{story_id}/comprehension/submit",
        json={"answers": [{"index": 0, "selected": "an apple"}]},
        headers=auth_headers,
    )

    assert response.status_code == 404


async def test_submit_comprehension_scores_correctly_and_awards_xp(
    client, onboarded_auth_headers, fake_ai_service
):
    generate_response = await client.post(
        "/api/ai/generate/mini-story", json={"level": "N5"}, headers=onboarded_auth_headers
    )
    story_id = generate_response.json()["id"]

    response = await client.post(
        f"/api/ai/mini-stories/{story_id}/comprehension/submit",
        json={
            "answers": [
                {"index": 0, "selected": "an apple"},  # correct
                {"index": 1, "selected": "school"},  # wrong
            ]
        },
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["score"] == 1
    assert body["total"] == 2
    assert body["xp_earned"] == 10
    assert body["total_xp"] == 10
    result_by_index = {r["index"]: r for r in body["results"]}
    assert result_by_index[0]["correct"] is True
    assert result_by_index[1]["correct"] is False
    assert result_by_index[1]["correct_answer"] == "the store"


async def test_submit_comprehension_for_unknown_story_returns_404(
    client, onboarded_auth_headers, fake_ai_service
):
    response = await client.post(
        "/api/ai/mini-stories/000000000000000000000000/comprehension/submit",
        json={"answers": [{"index": 0, "selected": "x"}]},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 404


async def test_submit_comprehension_not_owned_by_requester_returns_404(
    client, onboarded_auth_headers, fake_ai_service
):
    generate_response = await client.post(
        "/api/ai/generate/mini-story", json={"level": "N5"}, headers=onboarded_auth_headers
    )
    story_id = generate_response.json()["id"]

    other_register = await client.post(
        "/api/auth/register",
        json={"email": "someone-else@example.com", "password": "supersecret1"},
    )
    other_headers = {"Authorization": f"Bearer {other_register.json()['access_token']}"}
    await client.post(
        "/api/onboarding",
        json={
            "goals": ["jlpt"],
            "experience": "knows_hiragana",
            "preferred_level": "N5",
            "jlpt_target": "N5",
        },
        headers=other_headers,
    )

    response = await client.post(
        f"/api/ai/mini-stories/{story_id}/comprehension/submit",
        json={"answers": [{"index": 0, "selected": "an apple"}]},
        headers=other_headers,
    )

    assert response.status_code == 404


async def test_comprehension_results_feed_the_reading_skill(
    client, onboarded_auth_headers, fake_ai_service
):
    generate_response = await client.post(
        "/api/ai/generate/mini-story", json={"level": "N5"}, headers=onboarded_auth_headers
    )
    story_id = generate_response.json()["id"]

    await client.post(
        f"/api/ai/mini-stories/{story_id}/comprehension/submit",
        json={"answers": [{"index": 0, "selected": "an apple"}]},
        headers=onboarded_auth_headers,
    )

    progress_response = await client.get("/api/progress", headers=onboarded_auth_headers)

    reading = next(s for s in progress_response.json()["skills"] if s["category"] == "reading")
    assert reading["has_data"] is True
    assert reading["mastery"] == 1.0


async def test_submit_generated_question_requires_onboarding(client, auth_headers, fake_ai_service):
    generate_response = await client.post(
        "/api/ai/generate/vocabulary-question", json={"level": "N5"}, headers=auth_headers
    )
    question_id = generate_response.json()["id"]

    response = await client.post(
        f"/api/ai/generated-questions/{question_id}/submit",
        json={"selected": "to eat"},
        headers=auth_headers,
    )

    assert response.status_code == 404


async def test_submit_generated_question_scores_correctly_and_awards_xp(
    client, onboarded_auth_headers, fake_ai_service
):
    generate_response = await client.post(
        "/api/ai/generate/vocabulary-question", json={"level": "N5"}, headers=onboarded_auth_headers
    )
    question_id = generate_response.json()["id"]

    response = await client.post(
        f"/api/ai/generated-questions/{question_id}/submit",
        json={"selected": "to eat"},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["correct"] is True
    assert body["correct_answer"] == "to eat"
    assert body["xp_earned"] == 10
    assert body["total_xp"] == 10


async def test_submit_generated_question_with_wrong_answer_awards_no_xp(
    client, onboarded_auth_headers, fake_ai_service
):
    generate_response = await client.post(
        "/api/ai/generate/vocabulary-question", json={"level": "N5"}, headers=onboarded_auth_headers
    )
    question_id = generate_response.json()["id"]

    response = await client.post(
        f"/api/ai/generated-questions/{question_id}/submit",
        json={"selected": "to drink"},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["correct"] is False
    assert body["xp_earned"] == 0
    assert body["total_xp"] == 0


async def test_submit_generated_question_for_unknown_id_returns_404(
    client, onboarded_auth_headers, fake_ai_service
):
    response = await client.post(
        "/api/ai/generated-questions/000000000000000000000000/submit",
        json={"selected": "to eat"},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 404


async def test_submit_generated_question_feeds_the_vocabulary_skill(
    client, onboarded_auth_headers, fake_ai_service
):
    generate_response = await client.post(
        "/api/ai/generate/vocabulary-question", json={"level": "N5"}, headers=onboarded_auth_headers
    )
    question_id = generate_response.json()["id"]

    await client.post(
        f"/api/ai/generated-questions/{question_id}/submit",
        json={"selected": "to eat"},
        headers=onboarded_auth_headers,
    )

    mistakes_response = await client.get("/api/mistakes", headers=onboarded_auth_headers)
    assert mistakes_response.json() == []  # answered correctly, so no mistake recorded

    progress_response = await client.get("/api/progress", headers=onboarded_auth_headers)
    vocab = next(s for s in progress_response.json()["skills"] if s["category"] == "vocabulary")
    assert vocab["has_data"] is True
