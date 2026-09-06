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
  "created_at": "...",
  "updated_at": "..."
}
```

`estimated_level` is `null` until a later phase's test engine / learner model
has enough data to set it — never fabricated.

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

## Planned Routes (added phase by phase)

These are not implemented yet — listed here to reflect the intended surface
as the project grows:

| Route | Phase |
|---|---|
| `/api/activities`, `/api/vocabulary`, `/api/grammar`, `/api/kanji` | 3 |
| `/api/tests` | 4 |
| `/api/progress`, `/api/mistakes` | 5 |
| `/api/ai` | 6–7 |
| `/api/conversation` | 8 |
| `/api/speech` | 9 |
| `/api/recommendations` | 10 |

Each route follows `routes → services → repositories → MongoDB`; see
[ARCHITECTURE.md](ARCHITECTURE.md).
