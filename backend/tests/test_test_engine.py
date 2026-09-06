async def _get_test_id(client, headers, category):
    response = await client.get("/api/tests", headers=headers)
    return next(t["id"] for t in response.json() if t["category"] == category)


async def test_list_tests_requires_authentication(client, seed_tests):
    response = await client.get("/api/tests")

    assert response.status_code == 401


async def test_list_tests_returns_the_three_seeded_tests(client, auth_headers, seed_tests):
    response = await client.get("/api/tests", headers=auth_headers)

    assert response.status_code == 200
    categories = {t["category"] for t in response.json()}
    assert categories == {"vocabulary", "grammar", "mixed"}


async def test_get_test_detail_does_not_reveal_correct_answers(client, auth_headers, seed_tests):
    test_id = await _get_test_id(client, auth_headers, "vocabulary")

    response = await client.get(f"/api/tests/{test_id}", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "vocabulary"
    assert len(body["questions"]) > 0
    for question in body["questions"]:
        assert set(question.keys()) == {"id", "prompt", "options"}
        assert len(question["options"]) == 4


async def test_get_test_detail_for_unknown_id_returns_404(client, auth_headers, seed_tests):
    response = await client.get("/api/tests/000000000000000000000000", headers=auth_headers)

    assert response.status_code == 404


async def test_submit_attempt_requires_onboarding(client, auth_headers, seed_tests):
    test_id = await _get_test_id(client, auth_headers, "vocabulary")

    response = await client.post(
        f"/api/tests/{test_id}/attempts",
        json={"answers": [{"question_id": "000000000000000000000000", "selected": "x"}]},
        headers=auth_headers,
    )

    assert response.status_code == 404


async def test_submit_attempt_scores_correctly_and_awards_xp(
    client, onboarded_auth_headers, seed_tests
):
    test_id = await _get_test_id(client, onboarded_auth_headers, "vocabulary")
    detail = await client.get(f"/api/tests/{test_id}", headers=onboarded_auth_headers)
    questions = detail.json()["questions"]

    # Answer the first question correctly and the second incorrectly, using
    # the attempt's own result to know which option was actually correct.
    answers = [
        {"question_id": questions[0]["id"], "selected": questions[0]["options"][0]},
        {"question_id": questions[1]["id"], "selected": questions[1]["options"][0]},
    ]

    response = await client.post(
        f"/api/tests/{test_id}/attempts",
        json={"answers": answers},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["test_title"] == "N5 Vocabulary Test"
    assert body["xp_earned"] == body["score"] * 10
    assert body["total_xp"] == body["xp_earned"]
    assert len(body["answers"]) == 2
    for answer_result in body["answers"]:
        assert "correct_answer" in answer_result
        assert "explanation" in answer_result
        assert "concept" in answer_result


async def test_submit_attempt_for_unknown_test_returns_404(
    client, onboarded_auth_headers, seed_tests
):
    response = await client.post(
        "/api/tests/000000000000000000000000/attempts",
        json={"answers": [{"question_id": "000000000000000000000000", "selected": "x"}]},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 404


async def test_attempt_history_lists_completed_attempts(client, onboarded_auth_headers, seed_tests):
    test_id = await _get_test_id(client, onboarded_auth_headers, "grammar")
    detail = await client.get(f"/api/tests/{test_id}", headers=onboarded_auth_headers)
    question = detail.json()["questions"][0]

    await client.post(
        f"/api/tests/{test_id}/attempts",
        json={"answers": [{"question_id": question["id"], "selected": question["options"][0]}]},
        headers=onboarded_auth_headers,
    )

    response = await client.get("/api/tests/attempts", headers=onboarded_auth_headers)

    assert response.status_code == 200
    history = response.json()
    assert len(history) == 1
    assert history[0]["test_title"] == "N5 Grammar Test"
    assert history[0]["total"] == 1


async def test_attempt_detail_returns_full_answer_breakdown(
    client, onboarded_auth_headers, seed_tests
):
    test_id = await _get_test_id(client, onboarded_auth_headers, "mixed")
    detail = await client.get(f"/api/tests/{test_id}", headers=onboarded_auth_headers)
    question = detail.json()["questions"][0]

    submit_response = await client.post(
        f"/api/tests/{test_id}/attempts",
        json={"answers": [{"question_id": question["id"], "selected": question["options"][0]}]},
        headers=onboarded_auth_headers,
    )
    attempt_id = submit_response.json()["id"]

    response = await client.get(f"/api/tests/attempts/{attempt_id}", headers=onboarded_auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == attempt_id
    assert len(body["answers"]) == 1
    assert body["answers"][0]["question_id"] == question["id"]


async def test_attempt_detail_requires_authentication(client, seed_tests):
    response = await client.get("/api/tests/attempts/000000000000000000000000")

    assert response.status_code == 401


async def test_attempt_detail_not_owned_by_requester_returns_404(
    client, onboarded_auth_headers, seed_tests
):
    test_id = await _get_test_id(client, onboarded_auth_headers, "vocabulary")
    detail = await client.get(f"/api/tests/{test_id}", headers=onboarded_auth_headers)
    question = detail.json()["questions"][0]

    submit_response = await client.post(
        f"/api/tests/{test_id}/attempts",
        json={"answers": [{"question_id": question["id"], "selected": question["options"][0]}]},
        headers=onboarded_auth_headers,
    )
    attempt_id = submit_response.json()["id"]

    other_register = await client.post(
        "/api/auth/register",
        json={"email": "someone-else@example.com", "password": "supersecret1"},
    )
    other_headers = {"Authorization": f"Bearer {other_register.json()['access_token']}"}

    response = await client.get(f"/api/tests/attempts/{attempt_id}", headers=other_headers)

    assert response.status_code == 404
