async def test_list_vocabulary_requires_authentication(client, seed_content):
    response = await client.get("/api/vocabulary", params={"level": "N5"})

    assert response.status_code == 401


async def test_list_vocabulary_returns_seeded_items(client, auth_headers, seed_content):
    response = await client.get("/api/vocabulary", params={"level": "N5"}, headers=auth_headers)

    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 4
    assert all(item["level"] == "N5" for item in items)
    assert {"term", "reading", "meaning"} <= items[0].keys()


async def test_vocabulary_n5_has_no_duplicate_terms_or_meanings(client, auth_headers, seed_content):
    # Phase 14 grew this list substantially (12 -> 117) — a duplicate
    # "meaning" string would risk two visually-identical options in the
    # same quiz question, so this is a real correctness check, not just a
    # content-count assertion.
    response = await client.get("/api/vocabulary", params={"level": "N5"}, headers=auth_headers)

    items = response.json()
    assert len(items) >= 100
    terms = [item["term"] for item in items]
    meanings = [item["meaning"] for item in items]
    assert len(terms) == len(set(terms))
    assert len(meanings) == len(set(meanings))


async def test_list_grammar_returns_seeded_items(client, auth_headers, seed_content):
    response = await client.get("/api/grammar", params={"level": "N5"}, headers=auth_headers)

    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 4
    assert all(item["level"] == "N5" for item in items)
    assert {"example_sentence", "answer"} <= items[0].keys()


async def test_list_kanji_requires_authentication(client, seed_content):
    response = await client.get("/api/kanji", params={"level": "N5"})

    assert response.status_code == 401


async def test_list_kanji_returns_seeded_items(client, auth_headers, seed_content):
    response = await client.get("/api/kanji", params={"level": "N5"}, headers=auth_headers)

    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 60
    assert all(item["level"] == "N5" for item in items)
    assert {"character", "onyomi", "kunyomi", "meaning"} <= items[0].keys()


async def test_get_kanji_quiz_returns_questions_with_four_options(
    client, auth_headers, seed_content
):
    response = await client.get(
        "/api/activities/quiz",
        params={"category": "kanji", "level": "N5", "size": 3},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "kanji"
    assert len(body["questions"]) == 3
    for question in body["questions"]:
        assert len(question["options"]) == 4
        assert len(set(question["options"])) == 4


async def test_submit_kanji_quiz_scores_correctly_and_feeds_the_skill_model(
    client, onboarded_auth_headers, seed_content
):
    kanji_response = await client.get(
        "/api/kanji", params={"level": "N5"}, headers=onboarded_auth_headers
    )
    items = kanji_response.json()
    hi = next(item for item in items if item["character"] == "日")

    response = await client.post(
        "/api/activities/quiz/submit",
        json={
            "category": "kanji",
            "level": "N5",
            "answers": [{"item_id": hi["id"], "selected": hi["meaning"]}],
        },
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["correct_count"] == 1
    assert body["xp_earned"] == 10

    progress_response = await client.get("/api/progress", headers=onboarded_auth_headers)
    kanji_skill = next(s for s in progress_response.json()["skills"] if s["category"] == "kanji")
    assert kanji_skill["has_data"] is True
    assert kanji_skill["mastery"] == 1.0


async def test_get_kanji_flashcard_deck_returns_every_item(
    client, onboarded_auth_headers, seed_content
):
    kanji_response = await client.get(
        "/api/kanji", params={"level": "N5"}, headers=onboarded_auth_headers
    )
    all_items = kanji_response.json()

    response = await client.get(
        "/api/activities/flashcards",
        params={"category": "kanji", "level": "N5"},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    deck = response.json()
    assert {item["id"] for item in deck} == {item["id"] for item in all_items}


async def test_get_quiz_requires_authentication(client, seed_content):
    response = await client.get(
        "/api/activities/quiz", params={"category": "vocabulary", "level": "N5"}
    )

    assert response.status_code == 401


async def test_get_vocabulary_quiz_returns_questions_with_four_options(
    client, auth_headers, seed_content
):
    response = await client.get(
        "/api/activities/quiz",
        params={"category": "vocabulary", "level": "N5", "size": 3},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "vocabulary"
    assert len(body["questions"]) == 3
    for question in body["questions"]:
        assert len(question["options"]) == 4
        assert len(set(question["options"])) == 4


async def test_get_grammar_quiz_uses_example_sentence_as_prompt(client, auth_headers, seed_content):
    response = await client.get(
        "/api/activities/quiz",
        params={"category": "grammar", "level": "N5", "size": 2},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    for question in body["questions"]:
        assert "___" in question["prompt"]


async def test_submit_quiz_requires_onboarding(client, auth_headers, seed_content):
    response = await client.post(
        "/api/activities/quiz/submit",
        json={
            "category": "vocabulary",
            "level": "N5",
            "answers": [{"item_id": "000000000000000000000000", "selected": "to eat"}],
        },
        headers=auth_headers,
    )

    assert response.status_code == 404


async def test_submit_quiz_scores_correctly_and_awards_xp(
    client, onboarded_auth_headers, seed_content
):
    vocab_response = await client.get(
        "/api/vocabulary", params={"level": "N5"}, headers=onboarded_auth_headers
    )
    items = vocab_response.json()
    eat = next(item for item in items if item["meaning"] == "to eat")
    drink = next(item for item in items if item["meaning"] == "to drink")

    response = await client.post(
        "/api/activities/quiz/submit",
        json={
            "category": "vocabulary",
            "level": "N5",
            "answers": [
                {"item_id": eat["id"], "selected": "to eat"},  # correct
                {"item_id": drink["id"], "selected": "to eat"},  # wrong
            ],
        },
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["correct_count"] == 1
    assert body["total"] == 2
    assert body["xp_earned"] == 10
    assert body["total_xp"] == 10
    result_by_id = {r["item_id"]: r for r in body["results"]}
    assert result_by_id[eat["id"]]["correct"] is True
    assert result_by_id[drink["id"]]["correct"] is False
    assert result_by_id[drink["id"]]["correct_answer"] == "to drink"


async def test_quiz_xp_accumulates_on_the_profile_across_submissions(
    client, onboarded_auth_headers, seed_content
):
    vocab_response = await client.get(
        "/api/vocabulary", params={"level": "N5"}, headers=onboarded_auth_headers
    )
    item = vocab_response.json()[0]

    for _ in range(2):
        await client.post(
            "/api/activities/quiz/submit",
            json={
                "category": "vocabulary",
                "level": "N5",
                "answers": [{"item_id": item["id"], "selected": item["meaning"]}],
            },
            headers=onboarded_auth_headers,
        )

    profile_response = await client.get("/api/profile", headers=onboarded_auth_headers)

    assert profile_response.json()["xp"] == 20


async def test_flashcards_complete_requires_onboarding(client, auth_headers, seed_content):
    response = await client.post(
        "/api/activities/flashcards/complete",
        json={
            "category": "vocabulary",
            "level": "N5",
            "reviewed": [{"item_id": "000000000000000000000000", "known": True}],
        },
        headers=auth_headers,
    )

    assert response.status_code == 404


async def test_flashcards_complete_awards_xp_for_known_items(
    client, onboarded_auth_headers, seed_content
):
    vocab_response = await client.get(
        "/api/vocabulary", params={"level": "N5"}, headers=onboarded_auth_headers
    )
    items = vocab_response.json()[:3]

    response = await client.post(
        "/api/activities/flashcards/complete",
        json={
            "category": "vocabulary",
            "level": "N5",
            "reviewed": [
                {"item_id": items[0]["id"], "known": True},
                {"item_id": items[1]["id"], "known": True},
                {"item_id": items[2]["id"], "known": False},
            ],
        },
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["known_count"] == 2
    assert body["total"] == 3
    assert body["xp_earned"] == 10
    assert body["total_xp"] == 10


async def test_get_flashcard_deck_requires_authentication(client, seed_content):
    response = await client.get(
        "/api/activities/flashcards", params={"category": "vocabulary", "level": "N5"}
    )

    assert response.status_code == 401


async def test_get_flashcard_deck_returns_every_item_in_the_level(
    client, onboarded_auth_headers, seed_content
):
    vocab_response = await client.get(
        "/api/vocabulary", params={"level": "N5"}, headers=onboarded_auth_headers
    )
    all_items = vocab_response.json()

    response = await client.get(
        "/api/activities/flashcards",
        params={"category": "vocabulary", "level": "N5"},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    deck = response.json()
    assert {item["id"] for item in deck} == {item["id"] for item in all_items}


async def test_quiz_prioritizes_a_never_reviewed_concept_over_recently_correct_ones(
    client, onboarded_auth_headers, seed_content
):
    vocab_response = await client.get(
        "/api/vocabulary", params={"level": "N5"}, headers=onboarded_auth_headers
    )
    all_items = vocab_response.json()
    untouched = all_items[0]
    already_reviewed = all_items[1:]

    # Mark every item except `untouched` as freshly, correctly reviewed —
    # each gets a due date a day or more out.
    await client.post(
        "/api/activities/quiz/submit",
        json={
            "category": "vocabulary",
            "level": "N5",
            "answers": [
                {"item_id": item["id"], "selected": item["meaning"]} for item in already_reviewed
            ],
        },
        headers=onboarded_auth_headers,
    )

    response = await client.get(
        "/api/activities/quiz",
        params={"category": "vocabulary", "level": "N5", "size": 1},
        headers=onboarded_auth_headers,
    )

    assert response.status_code == 200
    question = response.json()["questions"][0]
    assert question["item_id"] == untouched["id"]


async def test_flashcard_deck_moves_recently_reviewed_items_toward_the_back(
    client, onboarded_auth_headers, seed_content
):
    vocab_response = await client.get(
        "/api/vocabulary", params={"level": "N5"}, headers=onboarded_auth_headers
    )
    all_items = vocab_response.json()
    freshly_reviewed = all_items[0]

    await client.post(
        "/api/activities/quiz/submit",
        json={
            "category": "vocabulary",
            "level": "N5",
            "answers": [
                {"item_id": freshly_reviewed["id"], "selected": freshly_reviewed["meaning"]}
            ],
        },
        headers=onboarded_auth_headers,
    )

    response = await client.get(
        "/api/activities/flashcards",
        params={"category": "vocabulary", "level": "N5"},
        headers=onboarded_auth_headers,
    )

    deck = response.json()
    assert deck[-1]["id"] == freshly_reviewed["id"]
