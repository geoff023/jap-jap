# Database

JapJap uses MongoDB, accessed asynchronously via the Motor driver
(`app/core/database.py`).

## Implemented Collections

### `users` (Phase 1)

Managed by `app/repositories/user_repository.py`.

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `email` | string | unique index |
| `hashed_password` | string | bcrypt hash, never returned by the API |
| `created_at` | datetime (UTC) | |

### `learner_profiles` (Phase 2)

Managed by `app/repositories/profile_repository.py`. One document per user,
keyed by `user_id` (not `_id`) so upserts are a single atomic
find-or-create-then-update.

| Field | Type | Notes |
|---|---|---|
| `user_id` | string | unique index; the owning user's `_id` as a string |
| `goals` | string[] | non-empty; see `LearningGoal` in `app/schemas/profile.py` |
| `experience` | string | `ExperienceLevel` enum value |
| `preferred_level` | string | `PracticeLevel` enum value (N5–N1 or `conversation`) — freely changeable |
| `estimated_level` | string \| null | `PracticeLevel` enum value; `null` until a learner model exists (Phase 5+) |
| `jlpt_target` | string \| null | `JLPTLevel` enum value; optional |
| `onboarding_completed` | bool | |
| `created_at`, `updated_at` | datetime (UTC) | |

## Planned Collections

These will be introduced as the relevant phase implements them:

```
learner_skills
learning_activities
vocabulary
grammar_concepts
kanji
tests
questions
test_attempts
mistakes
conversation_sessions
conversation_messages
speaking_attempts
progress_events
achievements
user_achievements
recommendations
ai_interactions
```

## Indexes

```
users.email (unique) — implemented, see UserRepository.ensure_indexes()
learner_profiles.user_id (unique) — implemented, see LearnerProfileRepository.ensure_indexes()
```

### Planned (minimum)

```
test_attempts.userId
mistakes.userId
progress_events.userId
conversation_sessions.userId
```

Indexes will be created via repository-layer setup code as each collection
is introduced, not added speculatively ahead of the features that use them.

## Level Fields

Three distinct, separately-stored fields on the learner profile
(implemented in Phase 2 as `preferred_level` / `estimated_level` /
`jlpt_target` — snake_case, matching the rest of the schema):

* `preferred_level` — what the learner wants to practise right now
* `estimated_level` — the system's current estimate of the learner's level
* `jlpt_target` — the learner's exam goal

These are never conflated. A learner can freely switch `preferred_level`
between N5–N1 or conversation mode with no lock, penalty, or forced
progression — enforced by `PATCH /api/profile` accepting any `PracticeLevel`
value at any time (see [API.md](API.md)).

## Local Development

MongoDB runs locally via Docker Compose:

```bash
docker compose up -d mongo
```

or against any local/remote MongoDB instance referenced by `MONGODB_URI` in
`.env`.
