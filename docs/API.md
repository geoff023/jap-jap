# API Reference

Base URL (local dev): `http://localhost:8000`

All application routes are namespaced under `/api`.

## Implemented

### `GET /api/health`

Returns API and database status. Always returns `200` — it never fails, even
if MongoDB is unreachable — so it can safely be used as a liveness check.

**Response**

```json
{
  "status": "ok",
  "database": "connected"
}
```

`database` is one of:

* `"connected"` — MongoDB responded to a ping
* `"unavailable"` — MongoDB is unreachable (the API itself is still up)

### `GET /`

Basic root endpoint, returns a static welcome message.

```json
{ "message": "JapJap API" }
```

### `POST /api/auth/register`

Creates a new user and returns an access token. `email` must be a valid
address; `password` must be 8–128 characters.

**Request**

```json
{ "email": "learner@example.com", "password": "supersecret1" }
```

**Response** (`201 Created`)

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": { "id": "...", "email": "learner@example.com", "created_at": "..." }
}
```

Errors: `409 Conflict` if the email is already registered, `422` if the
payload fails validation.

### `POST /api/auth/login`

Authenticates with email + password, returns the same shape as register.

Errors: `401 Unauthorized` for an unknown email or wrong password.

### `POST /api/auth/logout`

Requires `Authorization: Bearer <token>`. Returns `204 No Content`. Access
tokens are short-lived, stateless JWTs with no server-side session, so there
is nothing to invalidate yet — the client discards its token. Kept as a real,
protected endpoint so a token blacklist can be added later without an API
change.

Errors: `401 Unauthorized` if not authenticated.

### `GET /api/users/me`

Requires `Authorization: Bearer <token>`. Returns the current user.

```json
{ "id": "...", "email": "learner@example.com", "created_at": "..." }
```

Errors: `401 Unauthorized` if the token is missing, invalid, or expired.

### `POST /api/onboarding`

Requires `Authorization: Bearer <token>`. Creates (or overwrites) the
learner's profile and marks onboarding complete. Idempotent — safe to call
again, e.g. from a "redo onboarding" flow.

**Request**

```json
{
  "goals": ["anime_manga", "jlpt"],
  "experience": "knows_hiragana",
  "preferred_level": "N5",
  "jlpt_target": "N3"
}
```

* `goals`: non-empty list of `anime_manga | travel | conversation | jlpt |
  university | work | culture | fun`
* `experience`: one of `complete_beginner | knows_some_words |
  knows_hiragana | knows_hiragana_katakana | basic_grammar |
  previously_studied`
* `preferred_level`: one of `N5 | N4 | N3 | N2 | N1 | conversation`
* `jlpt_target`: one of `N5 | N4 | N3 | N2 | N1`, or `null` (optional — not
  every learner has an exam goal)

**Response** (`200 OK`) — a `LearnerProfilePublic` (see below).

Errors: `401 Unauthorized` if not authenticated, `422` if `goals` is empty or
a value isn't one of the allowed options.

### `GET /api/profile`

Requires `Authorization: Bearer <token>`. Returns the current learner
profile.

```json
{
  "user_id": "...",
  "goals": ["anime_manga", "jlpt"],
  "experience": "knows_hiragana",
  "preferred_level": "N5",
  "estimated_level": null,
  "jlpt_target": "N3",
  "onboarding_completed": true,
  "xp": 0,
  "created_at": "...",
  "updated_at": "..."
}
```

`estimated_level` is `null` until a later phase's test engine / learner model
has enough data to set it — never fabricated. `xp` only ever changes via
activity completion (see below), never via onboarding or profile edits.

Errors: `401 Unauthorized` if not authenticated, `404 Not Found` if the
learner hasn't completed onboarding yet.

### `PATCH /api/profile`

Requires `Authorization: Bearer <token>`. Partially updates the profile —
**only fields present in the body are changed**; this is how
`preferredLevel` is changed with no restriction, lock, or forced order
(e.g. `{"preferred_level": "N3"}` after being on `N5`, then back to `N4`,
etc. — all always `200 OK`). Send `"jlpt_target": null` to explicitly clear
the JLPT goal.

**Response** (`200 OK`) — the full updated `LearnerProfilePublic`.

Errors: `401 Unauthorized` if not authenticated, `404 Not Found` if the
learner hasn't completed onboarding yet (`POST /api/onboarding` first),
`422` for an invalid value.

### `GET /api/vocabulary`

Requires `Authorization: Bearer <token>`. Returns vocabulary items, optionally
filtered by `?level=N5`.

```json
[
  {
    "id": "...",
    "term": "食べる",
    "reading": "たべる",
    "meaning": "to eat",
    "level": "N5",
    "example_sentence": "朝ごはんを食べます。",
    "example_translation": "I eat breakfast."
  }
]
```

### `GET /api/grammar`

Requires `Authorization: Bearer <token>`. Returns grammar concepts, optionally
filtered by `?level=N5`. `example_sentence` contains a `___` blank;
`answer` is the word/phrase that fills it (used by the sentence-completion
quiz below, and shown directly here for flashcard study).

```json
[
  {
    "id": "...",
    "key": "particle-ha",
    "title": "Particle は (topic marker)",
    "level": "N5",
    "explanation": "は marks the topic of the sentence.",
    "example_sentence": "わたし___学生です。",
    "example_translation": "I am a student.",
    "answer": "は"
  }
]
```

### `GET /api/activities/quiz`

Requires `Authorization: Bearer <token>`. Generates a stateless multiple-choice
quiz — nothing is persisted until `/quiz/submit`. Query params: `category`
(`vocabulary` or `grammar`), `level` (e.g. `N5`), `size` (default 5, 1–20).
For `vocabulary` this is a **multiple choice** activity (term → meaning); for
`grammar` it's **sentence completion** (fill the blank in `example_sentence`).

```json
{
  "category": "vocabulary",
  "level": "N5",
  "questions": [
    { "item_id": "...", "prompt": "食べる", "options": ["to eat", "to go", "big", "water"] }
  ]
}
```

Options are shuffled and don't reveal which is correct — scoring happens
server-side on submit, from the same seeded content, not from anything the
client sends.

Errors: `401 Unauthorized` if not authenticated, `400 Bad Request` if the
category/level doesn't have at least 4 seeded items (1 correct + 3 distractors).

### `POST /api/activities/quiz/submit`

Requires `Authorization: Bearer <token>` **and a completed onboarding**
(profile must exist — XP has nowhere to accrue otherwise).

**Request**

```json
{
  "category": "vocabulary",
  "level": "N5",
  "answers": [{ "item_id": "...", "selected": "to eat" }]
}
```

**Response** (`200 OK`)

```json
{
  "correct_count": 1,
  "total": 1,
  "xp_earned": 10,
  "total_xp": 10,
  "results": [{ "item_id": "...", "correct": true, "correct_answer": "to eat" }]
}
```

10 XP per correct answer. Also records a `learning_activities` document
(`activity_type` is `multiple_choice` for vocabulary, `sentence_completion`
for grammar).

Errors: `401 Unauthorized` if not authenticated, `404 Not Found` if
onboarding hasn't been completed yet.

### `POST /api/activities/flashcards/complete`

Requires `Authorization: Bearer <token>` and a completed onboarding.
Flashcards are self-assessed (no server-checked "correct" answer) — the
client reports which items the learner marked as known.

**Request**

```json
{
  "category": "vocabulary",
  "level": "N5",
  "reviewed": [{ "item_id": "...", "known": true }]
}
```

**Response** (`200 OK`)

```json
{ "known_count": 1, "total": 1, "xp_earned": 5, "total_xp": 5 }
```

5 XP per item marked known (lower than quiz XP since it's self-graded, not
server-verified). Records a `learning_activities` document with
`activity_type: "flashcards"`.

Errors: `401 Unauthorized` if not authenticated, `404 Not Found` if
onboarding hasn't been completed yet.

### `GET /api/tests`

Requires `Authorization: Bearer <token>`. Lists the available tests (no
onboarding required — browsing is free, only submitting an attempt earns XP).

```json
[{ "id": "...", "title": "N5 Vocabulary Test", "category": "vocabulary", "level": "N5", "question_count": 12 }]
```

### `GET /api/tests/{test_id}`

Requires `Authorization: Bearer <token>`. Returns the test's questions in a
fixed order — options only, no `correct_answer`/`explanation` (those are
only revealed after submitting, in the per-answer result).

```json
{
  "id": "...",
  "title": "N5 Grammar Test",
  "category": "grammar",
  "level": "N5",
  "questions": [{ "id": "...", "prompt": "水___飲みます。", "options": ["を", "に", "で", "は"] }]
}
```

Errors: `401 Unauthorized` if not authenticated, `404 Not Found` for an
unknown test id.

### `POST /api/tests/{test_id}/attempts`

Requires `Authorization: Bearer <token>` and a completed onboarding.
Submits every answer for the test at once; scoring happens server-side by
re-fetching the referenced questions — the client's `selected` values are
never trusted as "already scored."

**Request**

```json
{ "answers": [{ "question_id": "...", "selected": "を" }] }
```

**Response** (`200 OK`)

```json
{
  "id": "...",
  "test_id": "...",
  "test_title": "N5 Grammar Test",
  "category": "grammar",
  "level": "N5",
  "score": 1,
  "total": 1,
  "xp_earned": 10,
  "total_xp": 130,
  "completed_at": "...",
  "answers": [
    {
      "question_id": "...",
      "concept": "particle-wo",
      "selected": "を",
      "correct": true,
      "correct_answer": "を",
      "explanation": "を marks the direct object of a verb."
    }
  ]
}
```

10 XP per correct answer (same rate as the Phase 3 quiz). Persists a
`test_attempts` document — this *is* the history entry, not a separate
`learning_activities` record.

Errors: `401 Unauthorized` if not authenticated, `404 Not Found` if
onboarding hasn't been completed yet or the test id is unknown.

### `GET /api/tests/attempts`

Requires `Authorization: Bearer <token>`. Lists the current user's past
attempts (newest first), each without the per-answer breakdown — see the
detail endpoint below for that.

```json
[{ "id": "...", "test_id": "...", "test_title": "N5 Grammar Test", "category": "grammar", "level": "N5", "score": 1, "total": 1, "xp_earned": 10, "completed_at": "..." }]
```

### `GET /api/tests/attempts/{attempt_id}`

Requires `Authorization: Bearer <token>`. Returns one attempt in full,
including the answer-by-answer breakdown (the "result page"). Ownership is
enforced — an attempt belonging to a different user returns `404`, not
`403`, so this endpoint never confirms whether an id merely exists.

Errors: `401 Unauthorized` if not authenticated, `404 Not Found` if the
attempt doesn't exist or belongs to someone else.

## Planned Routes (added phase by phase)

These are not implemented yet — listed here to reflect the intended surface
as the project grows:

| Route | Phase |
|---|---|
| `/api/kanji` | 3/13 |
| `/api/progress`, `/api/mistakes` | 5 |
| `/api/ai` | 6–7 |
| `/api/conversation` | 8 |
| `/api/speech` | 9 |
| `/api/recommendations` | 10 |

Each route follows `routes → services → repositories → MongoDB`; see
[ARCHITECTURE.md](ARCHITECTURE.md).
