async def test_list_scenarios_requires_authentication(client):
    response = await client.get("/api/conversation/scenarios")

    assert response.status_code == 401


async def test_list_scenarios_returns_the_three_scenarios_with_characters(client, auth_headers):
    response = await client.get("/api/conversation/scenarios", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    by_key = {s["key"]: s for s in body}
    assert set(by_key.keys()) == {"ramen_shop", "convenience_store", "train_station"}
    assert by_key["ramen_shop"]["character"]["name"] == "Momo"
    assert by_key["convenience_store"]["character"]["name"] == "Kiko"
    assert by_key["train_station"]["character"]["name"] == "Kenji"


async def test_start_session_requires_onboarding(client, auth_headers):
    response = await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=auth_headers,
    )

    assert response.status_code == 404


async def test_start_session_returns_the_static_opening_line(client, onboarded_auth_headers):
    response = await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["scenario"] == "ramen_shop"
    assert body["character"]["name"] == "Momo"
    assert len(body["messages"]) == 1
    assert body["messages"][0]["role"] == "character"
    assert body["messages"][0]["content"] == "いらっしゃいませ！何にしますか？"
    assert body["messages"][0]["translation"] == "Welcome! What would you like to order?"


async def test_list_sessions_returns_started_sessions(client, onboarded_auth_headers):
    await client.post(
        "/api/conversation/sessions",
        json={"scenario": "convenience_store", "level": "N5"},
        headers=onboarded_auth_headers,
    )

    response = await client.get("/api/conversation/sessions", headers=onboarded_auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["scenario"] == "convenience_store"
    assert body[0]["character_name"] == "Kiko"
    assert body[0]["message_count"] == 1


async def test_get_session_for_unknown_id_returns_404(client, onboarded_auth_headers):
    response = await client.get(
        "/api/conversation/sessions/000000000000000000000000", headers=onboarded_auth_headers
    )

    assert response.status_code == 404


async def test_get_session_not_owned_by_requester_returns_404(client, onboarded_auth_headers):
    start_response = await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=onboarded_auth_headers,
    )
    session_id = start_response.json()["id"]

    other_register = await client.post(
        "/api/auth/register",
        json={"email": "someone-else@example.com", "password": "supersecret1"},
    )
    other_headers = {"Authorization": f"Bearer {other_register.json()['access_token']}"}

    response = await client.get(f"/api/conversation/sessions/{session_id}", headers=other_headers)

    assert response.status_code == 404


async def test_send_message_requires_onboarding(client, auth_headers):
    response = await client.post(
        "/api/conversation/sessions/000000000000000000000000/messages",
        json={"content": "こんにちは"},
        headers=auth_headers,
    )

    assert response.status_code == 404


async def test_send_message_for_unknown_session_returns_404(client, onboarded_auth_headers):
    response = await client.post(
        "/api/conversation/sessions/000000000000000000000000/messages",
        json={"content": "こんにちは"},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 404


async def test_send_message_returns_ai_reply_and_awards_xp(
    client, onboarded_auth_headers, fake_ai_service
):
    start_response = await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=onboarded_auth_headers,
    )
    session_id = start_response.json()["id"]

    response = await client.post(
        f"/api/conversation/sessions/{session_id}/messages",
        json={"content": "ラーメンをください。"},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["user_message"]["content"] == "ラーメンをください。"
    assert body["character_message"]["role"] == "character"
    assert "Momo" in body["character_message"]["translation"]
    assert body["xp_earned"] == 3
    assert body["total_xp"] == 3

    call = next(c for c in fake_ai_service.calls if c[0] == "continue_conversation")
    assert call[1] == "Momo"
    assert call[2] == "Ramen Shop"
    assert call[3] == "N5"


async def test_send_message_uses_the_correct_character_per_scenario(
    client, onboarded_auth_headers, fake_ai_service
):
    start_response = await client.post(
        "/api/conversation/sessions",
        json={"scenario": "train_station", "level": "N4"},
        headers=onboarded_auth_headers,
    )
    session_id = start_response.json()["id"]

    await client.post(
        f"/api/conversation/sessions/{session_id}/messages",
        json={"content": "東京駅へ行きたいです。"},
        headers=onboarded_auth_headers,
    )

    call = next(c for c in fake_ai_service.calls if c[0] == "continue_conversation")
    assert call[1] == "Kenji"
    assert call[2] == "Train Station"


async def test_send_message_accumulates_history_across_turns(
    client, onboarded_auth_headers, fake_ai_service
):
    start_response = await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=onboarded_auth_headers,
    )
    session_id = start_response.json()["id"]

    await client.post(
        f"/api/conversation/sessions/{session_id}/messages",
        json={"content": "ラーメンをください。"},
        headers=onboarded_auth_headers,
    )
    await client.post(
        f"/api/conversation/sessions/{session_id}/messages",
        json={"content": "水もお願いします。"},
        headers=onboarded_auth_headers,
    )

    calls = [c for c in fake_ai_service.calls if c[0] == "continue_conversation"]
    assert len(calls) == 2
    # First turn: no prior history besides the opening line.
    assert len(calls[0][4]) == 1
    assert calls[0][4][0]["role"] == "character"
    # Second turn: history now includes the opening line plus the first
    # exchange (user message + character reply) — this is what keeps the
    # character consistent across turns despite each Gemini call being
    # stateless.
    assert len(calls[1][4]) == 3
    assert [turn["role"] for turn in calls[1][4]] == ["character", "user", "character"]


async def test_send_message_increases_session_message_count(
    client, onboarded_auth_headers, fake_ai_service
):
    start_response = await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=onboarded_auth_headers,
    )
    session_id = start_response.json()["id"]

    await client.post(
        f"/api/conversation/sessions/{session_id}/messages",
        json={"content": "ラーメンをください。"},
        headers=onboarded_auth_headers,
    )

    sessions_response = await client.get(
        "/api/conversation/sessions", headers=onboarded_auth_headers
    )
    assert sessions_response.json()[0]["message_count"] == 3

    detail_response = await client.get(
        f"/api/conversation/sessions/{session_id}", headers=onboarded_auth_headers
    )
    assert len(detail_response.json()["messages"]) == 3


async def test_send_message_returns_502_when_ai_fails(
    client, onboarded_auth_headers, fake_ai_service
):
    start_response = await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=onboarded_auth_headers,
    )
    session_id = start_response.json()["id"]
    fake_ai_service.should_fail = True

    response = await client.post(
        f"/api/conversation/sessions/{session_id}/messages",
        json={"content": "ラーメンをください。"},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 502


async def test_send_message_for_session_not_owned_by_requester_returns_404(
    client, onboarded_auth_headers, fake_ai_service
):
    start_response = await client.post(
        "/api/conversation/sessions",
        json={"scenario": "ramen_shop", "level": "N5"},
        headers=onboarded_auth_headers,
    )
    session_id = start_response.json()["id"]

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
        f"/api/conversation/sessions/{session_id}/messages",
        json={"content": "こんにちは"},
        headers=other_headers,
    )

    assert response.status_code == 404
