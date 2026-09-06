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
| `xp` | int | default 0; only changed by `LearnerProfileRepository.increment_xp()` (activity completion), never by onboarding/profile-edit upserts |
| `created_at`, `updated_at` | datetime (UTC) | |

### `vocabulary` (Phase 3)

Managed by `app/repositories/vocabulary_repository.py`. Seeded once at app
startup from `app/core/seed_data.py` if the collection is empty
(`VOCABULARY_N5` — 12 original N5 words; no massive content library yet,
broader coverage is Phase 13's job).

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `term` | string | Japanese word, e.g. 食べる |
| `reading` | string | kana reading |
| `meaning` | string | English meaning — also the "correct answer" for the vocabulary multiple-choice quiz |
| `level` | string | `JLPTLevel` value |
| `example_sentence`, `example_translation` | string \| null | |

### `grammar_concepts` (Phase 3)

Managed by `app/repositories/grammar_repository.py`. Seeded from
`GRAMMAR_N5` (8 original N5 particle/conjugation points) the same way as
vocabulary.

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `key` | string | short identifier, e.g. `particle-ha` |
| `title` | string | |
| `level` | string | `JLPTLevel` value |
| `explanation` | string | |
| `example_sentence` | string | contains a `___` blank |
| `example_translation` | string | |
| `answer` | string | the word/phrase that fills the blank — the "correct answer" for the grammar sentence-completion quiz |

### `learning_activities` (Phase 3)

Managed by `app/repositories/activity_repository.py`. Append-only log of
completed activities — never updated after insert.

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `user_id` | string | indexed |
| `category` | string | `vocabulary` \| `grammar` |
| `activity_type` | string | `multiple_choice` \| `sentence_completion` \| `flashcards` |
| `level` | string | |
| `correct_count`/`total` (quiz) or `known_count`/`total` (flashcards) | int | |
| `xp_earned` | int | |
| `created_at` | datetime (UTC) | |

### `questions` (Phase 4)

Managed by `app/repositories/question_repository.py`. Derived deterministically
from `VOCABULARY_N5`/`GRAMMAR_N5` at seed time (`app/core/test_seed_data.py`)
— one source of truth for N5 content, not a separately authored question
bank. Standalone/reusable: referenced by `tests.question_ids`, not owned by
a single test.

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `category` | string | `vocabulary` \| `grammar` |
| `level` | string | `JLPTLevel` value |
| `concept` | string | the vocabulary term or grammar `key` — links a wrong answer back to *what* the learner got wrong, for a future learner model to aggregate |
| `difficulty` | string | `easy` \| `medium` \| `hard` (all seeded as `easy` for now) |
| `prompt` | string | question text or sentence-with-blank |
| `options` | string[] | 4 options, correct answer's position varies by question |
| `correct_answer` | string | never returned by `GET /api/tests/{id}` — only revealed per-answer after `POST .../attempts` |
| `explanation` | string | shown after answering |

### `tests` (Phase 4)

Managed by `app/repositories/test_repository.py`. Three tests seeded once at
startup (see `app/core/test_seed_data.py`): "N5 Vocabulary Test", "N5
Grammar Test", "N5 Mixed Test" — created system-side, not user-authored;
there is no test-authoring UI yet.

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `title` | string | |
| `category` | string | `vocabulary` \| `grammar` \| `mixed` |
| `level` | string | `JLPTLevel` value |
| `question_ids` | string[] | ordered; resolved against `questions` at request time, not denormalized |

### `test_attempts` (Phase 4)

Managed by `app/repositories/test_attempt_repository.py`. One document per
completed attempt (submitted all-at-once, like the Phase 3 quiz — there's no
"in progress" state); this collection *is* the test history and result-page
data, with each answer already carrying its `concept` for a future learner
model to connect results to skills.

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `user_id` | string | indexed |
| `test_id` | string | |
| `test_title`, `category`, `level` | string | denormalized from the test at submission time, so history/results don't break if a test is ever edited |
| `answers` | array | each: `question_id`, `concept`, `selected`, `correct`, `correct_answer`, `explanation` |
| `score`, `total` | int | |
| `xp_earned` | int | |
| `completed_at` | datetime (UTC) | |

## Planned Collections

These will be introduced as the relevant phase implements them:

```
learner_skills
kanji
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
vocabulary.level — implemented, see VocabularyRepository.ensure_indexes()
grammar_concepts.level — implemented, see GrammarRepository.ensure_indexes()
learning_activities.user_id — implemented, see ActivityRepository.ensure_indexes()
questions.category, questions.level — implemented, see QuestionRepository.ensure_indexes()
tests.category, tests.level — implemented, see TestRepository.ensure_indexes()
test_attempts.user_id — implemented, see TestAttemptRepository.ensure_indexes()
```

### Planned (minimum)

```
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
