async def _submit_vocab_quiz_answer(client, headers, correct: bool):
    vocab_response = await client.get("/api/vocabulary", params={"level": "N5"}, headers=headers)
    item = vocab_response.json()[0]
    selected = item["meaning"] if correct else "definitely not the meaning"
    await client.post(
        "/api/activities/quiz/submit",
        json={
            "category": "vocabulary",
            "level": "N5",
            "answers": [{"item_id": item["id"], "selected": selected}],
        },
        headers=headers,
    )
    return item


async def test_progress_requires_authentication(client):
    response = await client.get("/api/progress")

    assert response.status_code == 401


async def test_progress_reports_not_enough_data_with_no_activity(client, onboarded_auth_headers):
    response = await client.get("/api/progress", headers=onboarded_auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["overall"]["has_data"] is False
    assert body["overall"]["mastery"] is None
    for skill in body["skills"]:
        assert skill["has_data"] is False
        assert skill["mastery"] is None
    assert body["estimated_jlpt_readiness"]["has_data"] is False


async def test_progress_tracks_vocabulary_mastery_after_a_quiz(
    client, onboarded_auth_headers, seed_content
):
    await _submit_vocab_quiz_answer(client, onboarded_auth_headers, correct=True)

    response = await client.get("/api/progress", headers=onboarded_auth_headers)

    assert response.status_code == 200
    body = response.json()
    vocab = next(s for s in body["skills"] if s["category"] == "vocabulary")
    assert vocab["has_data"] is True
    assert vocab["mastery"] == 1.0
    assert vocab["concepts_tracked"] == 1
    grammar = next(s for s in body["skills"] if s["category"] == "grammar")
    assert grammar["has_data"] is False
    assert body["overall"]["has_data"] is True
    assert body["overall"]["mastery"] == 1.0


async def test_progress_categories_without_a_data_source_report_not_enough_data(
    client, onboarded_auth_headers, seed_content
):
    await _submit_vocab_quiz_answer(client, onboarded_auth_headers, correct=True)

    response = await client.get("/api/progress", headers=onboarded_auth_headers)

    body = response.json()
    for category in ["kanji", "reading", "listening", "speaking", "conversation"]:
        skill = next(s for s in body["skills"] if s["category"] == category)
        assert skill["has_data"] is False
        assert skill["mastery"] is None


async def test_estimated_readiness_requires_enough_attempts(
    client, onboarded_auth_headers, seed_content
):
    # onboarded_auth_headers sets jlpt_target=N5, but only 1 attempt so far —
    # below MIN_ATTEMPTS_FOR_READINESS.
    await _submit_vocab_quiz_answer(client, onboarded_auth_headers, correct=True)

    response = await client.get("/api/progress", headers=onboarded_auth_headers)

    body = response.json()
    assert body["estimated_jlpt_readiness"]["has_data"] is False
    assert body["estimated_jlpt_readiness"]["jlpt_target"] == "N5"


async def test_estimated_readiness_appears_after_enough_attempts(
    client, onboarded_auth_headers, seed_content
):
    for _ in range(5):
        await _submit_vocab_quiz_answer(client, onboarded_auth_headers, correct=True)

    response = await client.get("/api/progress", headers=onboarded_auth_headers)

    body = response.json()
    assert body["estimated_jlpt_readiness"]["has_data"] is True
    assert body["estimated_jlpt_readiness"]["score"] == 1.0


async def test_mistakes_requires_authentication(client):
    response = await client.get("/api/mistakes")

    assert response.status_code == 401


async def test_mistakes_empty_when_nothing_missed(client, onboarded_auth_headers, seed_content):
    await _submit_vocab_quiz_answer(client, onboarded_auth_headers, correct=True)

    response = await client.get("/api/mistakes", headers=onboarded_auth_headers)

    assert response.status_code == 200
    assert response.json() == []


async def test_mistakes_lists_recurring_wrong_answers(client, onboarded_auth_headers, seed_content):
    item = None
    for _ in range(3):
        item = await _submit_vocab_quiz_answer(client, onboarded_auth_headers, correct=False)

    response = await client.get("/api/mistakes", headers=onboarded_auth_headers)

    assert response.status_code == 200
    mistakes = response.json()
    assert len(mistakes) == 1
    assert mistakes[0]["concept"] == item["term"]
    assert mistakes[0]["category"] == "vocabulary"
    assert mistakes[0]["occurrences"] == 3
    assert mistakes[0]["mastery"] == 0.0


async def test_mistakes_mastery_reflects_a_mix_of_right_and_wrong(
    client, onboarded_auth_headers, seed_content
):
    await _submit_vocab_quiz_answer(client, onboarded_auth_headers, correct=False)
    await _submit_vocab_quiz_answer(client, onboarded_auth_headers, correct=True)

    response = await client.get("/api/mistakes", headers=onboarded_auth_headers)

    mistakes = response.json()
    assert len(mistakes) == 1
    assert mistakes[0]["occurrences"] == 1
    assert mistakes[0]["mastery"] == 0.5


async def test_flashcards_and_test_engine_results_also_feed_the_skill_model(
    client, onboarded_auth_headers, seed_content, seed_tests
):
    vocab_response = await client.get(
        "/api/vocabulary", params={"level": "N5"}, headers=onboarded_auth_headers
    )
    item = vocab_response.json()[0]
    await client.post(
        "/api/activities/flashcards/complete",
        json={
            "category": "vocabulary",
            "level": "N5",
            "reviewed": [{"item_id": item["id"], "known": False}],
        },
        headers=onboarded_auth_headers,
    )

    tests_response = await client.get("/api/tests", headers=onboarded_auth_headers)
    grammar_test_id = next(t["id"] for t in tests_response.json() if t["category"] == "grammar")
    test_detail = await client.get(f"/api/tests/{grammar_test_id}", headers=onboarded_auth_headers)
    question = test_detail.json()["questions"][0]
    await client.post(
        f"/api/tests/{grammar_test_id}/attempts",
        json={"answers": [{"question_id": question["id"], "selected": question["options"][0]}]},
        headers=onboarded_auth_headers,
    )

    response = await client.get("/api/progress", headers=onboarded_auth_headers)

    body = response.json()
    vocab = next(s for s in body["skills"] if s["category"] == "vocabulary")
    grammar = next(s for s in body["skills"] if s["category"] == "grammar")
    assert vocab["has_data"] is True
    assert grammar["has_data"] is True
