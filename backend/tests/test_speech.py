FAKE_AUDIO = b"fake-audio-bytes"


async def test_list_prompts_requires_authentication(client):
    response = await client.get("/api/speech/prompts")

    assert response.status_code == 401


async def test_list_prompts_returns_all_prompts(client, auth_headers):
    response = await client.get("/api/speech/prompts", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 9
    greeting = next(p for p in body if p["key"] == "n5-greeting")
    assert greeting["target_text"] == "おはようございます"
    assert greeting["target_translation"] == "Good morning."


async def test_list_prompts_filters_by_level(client, auth_headers):
    response = await client.get("/api/speech/prompts?level=N4", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert all(p["level"] == "N4" for p in body)


async def test_submit_attempt_requires_onboarding(client, auth_headers, fake_stt_service):
    response = await client.post(
        "/api/speech/attempts",
        data={"prompt_key": "n5-greeting"},
        files={"audio": ("clip.webm", FAKE_AUDIO, "audio/webm")},
        headers=auth_headers,
    )

    assert response.status_code == 404


async def test_submit_attempt_scores_a_correct_pronunciation(
    client, onboarded_auth_headers, fake_stt_service
):
    fake_stt_service.transcript = "おはようございます"

    response = await client.post(
        "/api/speech/attempts",
        data={"prompt_key": "n5-greeting"},
        files={"audio": ("clip.webm", FAKE_AUDIO, "audio/webm")},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["transcript"] == "おはようございます"
    assert body["target_text"] == "おはようございます"
    assert body["correct"] is True
    assert body["similarity"] == 1.0
    assert body["xp_earned"] == 10
    assert body["total_xp"] == 10

    call = next(c for c in fake_stt_service.calls if c[0] == "transcribe")
    assert call[1] == len(FAKE_AUDIO)
    assert call[2] == "audio/webm"


async def test_submit_attempt_scores_an_incorrect_pronunciation(
    client, onboarded_auth_headers, fake_stt_service
):
    fake_stt_service.transcript = "こんばんは"

    response = await client.post(
        "/api/speech/attempts",
        data={"prompt_key": "n5-greeting"},
        files={"audio": ("clip.webm", FAKE_AUDIO, "audio/webm")},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["correct"] is False
    assert body["xp_earned"] == 0
    assert body["total_xp"] == 0


async def test_submit_attempt_tolerates_trailing_punctuation_differences(
    client, onboarded_auth_headers, fake_stt_service
):
    fake_stt_service.transcript = "おはようございます。"

    response = await client.post(
        "/api/speech/attempts",
        data={"prompt_key": "n5-greeting"},
        files={"audio": ("clip.webm", FAKE_AUDIO, "audio/webm")},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["correct"] is True


async def test_submit_attempt_for_unknown_prompt_returns_404(
    client, onboarded_auth_headers, fake_stt_service
):
    response = await client.post(
        "/api/speech/attempts",
        data={"prompt_key": "not-a-real-prompt"},
        files={"audio": ("clip.webm", FAKE_AUDIO, "audio/webm")},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 404


async def test_submit_attempt_rejects_an_unsupported_audio_format(
    client, onboarded_auth_headers, fake_stt_service
):
    response = await client.post(
        "/api/speech/attempts",
        data={"prompt_key": "n5-greeting"},
        files={"audio": ("clip.txt", b"not audio", "text/plain")},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 422


async def test_submit_attempt_returns_502_when_the_provider_fails(
    client, onboarded_auth_headers, fake_stt_service
):
    fake_stt_service.should_fail = True

    response = await client.post(
        "/api/speech/attempts",
        data={"prompt_key": "n5-greeting"},
        files={"audio": ("clip.webm", FAKE_AUDIO, "audio/webm")},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 502


async def test_submit_attempt_returns_503_without_a_configured_key(client, onboarded_auth_headers):
    from app.core.config import Settings, get_settings
    from app.main import app

    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None, stt_api_key=None)
    try:
        response = await client.post(
            "/api/speech/attempts",
            data={"prompt_key": "n5-greeting"},
            files={"audio": ("clip.webm", FAKE_AUDIO, "audio/webm")},
            headers=onboarded_auth_headers,
        )
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 503


async def test_list_attempts_returns_past_attempts(
    client, onboarded_auth_headers, fake_stt_service
):
    await client.post(
        "/api/speech/attempts",
        data={"prompt_key": "n5-greeting"},
        files={"audio": ("clip.webm", FAKE_AUDIO, "audio/webm")},
        headers=onboarded_auth_headers,
    )

    response = await client.get("/api/speech/attempts", headers=onboarded_auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["prompt_key"] == "n5-greeting"
    assert body[0]["correct"] is True


async def test_speaking_attempts_feed_the_speaking_skill(
    client, onboarded_auth_headers, fake_stt_service
):
    await client.post(
        "/api/speech/attempts",
        data={"prompt_key": "n5-greeting"},
        files={"audio": ("clip.webm", FAKE_AUDIO, "audio/webm")},
        headers=onboarded_auth_headers,
    )

    progress_response = await client.get("/api/progress", headers=onboarded_auth_headers)

    speaking = next(s for s in progress_response.json()["skills"] if s["category"] == "speaking")
    assert speaking["has_data"] is True
    assert speaking["mastery"] == 1.0
