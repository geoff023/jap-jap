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

## Planned Collections

These will be introduced as the relevant phase implements them:

```
learner_profiles
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
```

### Planned (minimum)

```
learner_profiles.userId
test_attempts.userId
mistakes.userId
progress_events.userId
conversation_sessions.userId
```

Indexes will be created via repository-layer setup code as each collection
is introduced, not added speculatively ahead of the features that use them.

## Level Fields

Three distinct, separately-stored fields on the learner profile (Phase 2+):

* `preferredLevel` — what the learner wants to practise right now
* `estimatedLevel` — the system's current estimate of the learner's level
* `jlptTarget` — the learner's exam goal

These are never conflated. A learner can freely switch `preferredLevel`
between N5–N1 or conversation mode with no lock, penalty, or forced
progression.

## Local Development

MongoDB runs locally via Docker Compose:

```bash
docker compose up -d mongo
```

or against any local/remote MongoDB instance referenced by `MONGODB_URI` in
`.env`.
