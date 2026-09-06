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

## Planned Routes (added phase by phase)

These are not implemented yet — listed here to reflect the intended surface
as the project grows:

| Route | Phase |
|---|---|
| `/api/onboarding`, `/api/profile` | 2 |
| `/api/activities`, `/api/vocabulary`, `/api/grammar`, `/api/kanji` | 3 |
| `/api/tests` | 4 |
| `/api/progress`, `/api/mistakes` | 5 |
| `/api/ai` | 6–7 |
| `/api/conversation` | 8 |
| `/api/speech` | 9 |
| `/api/recommendations` | 10 |

Each route follows `routes → services → repositories → MongoDB`; see
[ARCHITECTURE.md](ARCHITECTURE.md).
