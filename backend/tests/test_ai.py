async def test_explain_grammar_requires_authentication(client, fake_ai_service):
    response = await client.post("/api/ai/explain/grammar", json={"concept": "particle-ha"})

    assert response.status_code == 401


async def test_explain_grammar_returns_a_validated_explanation(
    client, auth_headers, fake_ai_service
):
    response = await client.post(
        "/api/ai/explain/grammar",
        json={"concept": "particle-ha", "context": "わたしは学生です。"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["concept"] == "particle-ha"
    assert body["explanation"]
    assert body["example_sentence"]
    assert body["example_translation"]
    assert fake_ai_service.calls == [("grammar", "particle-ha", "わたしは学生です。")]


async def test_explain_vocabulary_returns_a_validated_explanation(
    client, auth_headers, fake_ai_service
):
    response = await client.post(
        "/api/ai/explain/vocabulary",
        json={"term": "食べる"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["term"] == "食べる"
    assert body["meaning"]
    assert fake_ai_service.calls == [("vocabulary", "食べる", None)]


async def test_explain_mistake_returns_a_validated_explanation(
    client, auth_headers, fake_ai_service
):
    response = await client.post(
        "/api/ai/explain/mistake",
        json={
            "category": "grammar",
            "concept": "particle-ni",
            "user_answer": "で",
            "correct_answer": "に",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["concept"] == "particle-ni"
    assert "に" in body["explanation"]
    assert body["tip"]


async def test_explain_grammar_rejects_an_empty_concept(client, auth_headers, fake_ai_service):
    response = await client.post(
        "/api/ai/explain/grammar", json={"concept": ""}, headers=auth_headers
    )

    assert response.status_code == 422


async def test_explain_grammar_returns_502_when_the_ai_service_fails(
    client, auth_headers, fake_ai_service
):
    fake_ai_service.should_fail = True

    response = await client.post(
        "/api/ai/explain/grammar", json={"concept": "particle-ha"}, headers=auth_headers
    )

    assert response.status_code == 502


async def test_ai_endpoints_return_503_without_a_configured_api_key(client, auth_headers):
    # No fake_ai_service override here — exercises the real get_ai_service
    # dependency, which must refuse cleanly (not crash) when GEMINI_API_KEY
    # isn't set, exactly as it won't be in CI or a fresh local checkout.
    # Settings is overridden directly (rather than relying on the ambient
    # environment) so this test is deterministic even when a developer has
    # their own real key in a local .env for manual testing.
    from app.core.config import Settings, get_settings
    from app.main import app

    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None, gemini_api_key=None)
    try:
        response = await client.post(
            "/api/ai/explain/grammar", json={"concept": "particle-ha"}, headers=auth_headers
        )
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 503


async def test_successful_ai_calls_are_logged_as_interactions(
    client, auth_headers, fake_ai_service
):
    from app.core.database import get_database
    from app.repositories.ai_interaction_repository import AIInteractionRepository

    await client.post("/api/ai/explain/vocabulary", json={"term": "食べる"}, headers=auth_headers)

    me_response = await client.get("/api/users/me", headers=auth_headers)
    user_id = me_response.json()["id"]

    interactions = await AIInteractionRepository(get_database()).list_by_user(user_id)

    assert len(interactions) == 1
    assert interactions[0]["interaction_type"] == "vocabulary_explanation"
    assert interactions[0]["concept"] == "食べる"


async def test_failed_ai_calls_are_not_logged(client, auth_headers, fake_ai_service):
    from app.core.database import get_database
    from app.repositories.ai_interaction_repository import AIInteractionRepository

    fake_ai_service.should_fail = True
    await client.post("/api/ai/explain/vocabulary", json={"term": "食べる"}, headers=auth_headers)

    me_response = await client.get("/api/users/me", headers=auth_headers)
    user_id = me_response.json()["id"]

    interactions = await AIInteractionRepository(get_database()).list_by_user(user_id)

    assert interactions == []
