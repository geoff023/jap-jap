DEFAULT_ONBOARDING = {
    "goals": ["anime_manga", "jlpt"],
    "experience": "knows_hiragana",
    "preferred_level": "N5",
    "jlpt_target": "N3",
}


async def test_onboarding_requires_authentication(client):
    response = await client.post("/api/onboarding", json=DEFAULT_ONBOARDING)

    assert response.status_code == 401


async def test_onboarding_creates_a_profile(client, auth_headers):
    response = await client.post("/api/onboarding", json=DEFAULT_ONBOARDING, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["goals"] == ["anime_manga", "jlpt"]
    assert body["experience"] == "knows_hiragana"
    assert body["preferred_level"] == "N5"
    assert body["jlpt_target"] == "N3"
    assert body["estimated_level"] is None
    assert body["onboarding_completed"] is True


async def test_onboarding_requires_at_least_one_goal(client, auth_headers):
    payload = {**DEFAULT_ONBOARDING, "goals": []}

    response = await client.post("/api/onboarding", json=payload, headers=auth_headers)

    assert response.status_code == 422


async def test_onboarding_allows_no_jlpt_target(client, auth_headers):
    payload = {**DEFAULT_ONBOARDING, "jlpt_target": None}

    response = await client.post("/api/onboarding", json=payload, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["jlpt_target"] is None


async def test_get_profile_requires_authentication(client):
    response = await client.get("/api/profile")

    assert response.status_code == 401


async def test_get_profile_before_onboarding_returns_404(client, auth_headers):
    response = await client.get("/api/profile", headers=auth_headers)

    assert response.status_code == 404


async def test_get_profile_after_onboarding_returns_it(client, auth_headers):
    await client.post("/api/onboarding", json=DEFAULT_ONBOARDING, headers=auth_headers)

    response = await client.get("/api/profile", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["preferred_level"] == "N5"


async def test_patch_profile_before_onboarding_returns_404(client, auth_headers):
    response = await client.patch(
        "/api/profile", json={"preferred_level": "N4"}, headers=auth_headers
    )

    assert response.status_code == 404


async def test_preferred_level_can_change_without_restriction(client, auth_headers):
    await client.post("/api/onboarding", json=DEFAULT_ONBOARDING, headers=auth_headers)

    # N5 -> N4 -> N3 -> N5 -> N4 -> conversation, with no lock or forced order.
    for level in ["N4", "N3", "N5", "N4", "conversation"]:
        response = await client.patch(
            "/api/profile", json={"preferred_level": level}, headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["preferred_level"] == level


async def test_patch_profile_only_changes_provided_fields(client, auth_headers):
    await client.post("/api/onboarding", json=DEFAULT_ONBOARDING, headers=auth_headers)

    response = await client.patch(
        "/api/profile", json={"preferred_level": "N2"}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["preferred_level"] == "N2"
    # Untouched fields from the original onboarding payload persist.
    assert body["experience"] == "knows_hiragana"
    assert body["jlpt_target"] == "N3"
    assert body["goals"] == ["anime_manga", "jlpt"]


async def test_patch_profile_can_clear_jlpt_target(client, auth_headers):
    await client.post("/api/onboarding", json=DEFAULT_ONBOARDING, headers=auth_headers)

    response = await client.patch("/api/profile", json={"jlpt_target": None}, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["jlpt_target"] is None


async def test_profile_persists_across_requests(client, auth_headers):
    await client.post("/api/onboarding", json=DEFAULT_ONBOARDING, headers=auth_headers)
    await client.patch("/api/profile", json={"preferred_level": "N1"}, headers=auth_headers)

    response = await client.get("/api/profile", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["preferred_level"] == "N1"
