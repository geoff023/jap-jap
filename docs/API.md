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

## Planned Routes (added phase by phase)

These are not implemented yet — listed here to reflect the intended surface
as the project grows:

| Route | Phase |
|---|---|
| `/api/auth` | 1 — Authentication |
| `/api/users`, `/api/onboarding`, `/api/profile` | 1–2 |
| `/api/activities`, `/api/vocabulary`, `/api/grammar`, `/api/kanji` | 3 |
| `/api/tests` | 4 |
| `/api/progress`, `/api/mistakes` | 5 |
| `/api/ai` | 6–7 |
| `/api/conversation` | 8 |
| `/api/speech` | 9 |
| `/api/recommendations` | 10 |

Each route follows `routes → services → repositories → MongoDB`; see
[ARCHITECTURE.md](ARCHITECTURE.md).
