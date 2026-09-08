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
| `source` | string \| absent | `"ai_generated"` for content from `/api/ai/generate/*` (Phase 7); absent (not `"seed"`) for the original Phase 4 seed data |

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

### `learner_skills` (Phase 5)

Managed by `app/repositories/skill_repository.py`. One document per
`(user_id, category, concept)` — the single source of truth for skill
mastery, mistakes, and estimated JLPT readiness, all computed by aggregating
these documents. Updated by `ActivityService` (Phase 3 quiz/flashcards) and
`TestService` (Phase 4 attempts) as a side effect of scoring — there's no
separate "sync" step. A concept is the same skill (e.g. 食べる, or
`particle-ha`) whichever activity type it was practiced through.

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `user_id` | string | |
| `category` | string | `vocabulary` \| `grammar` (only categories with a data source so far) |
| `concept` | string | vocabulary `term` or grammar `key` |
| `correct_count` | int | absent (not zero) until the first correct answer — `$inc` creates it |
| `incorrect_count` | int | absent until the first wrong answer |
| `last_seen` | datetime (UTC) | updated on every result, right or wrong |
| `created_at` | datetime (UTC) | |

Mastery for a concept is always computed on read as
`correct_count / (correct_count + incorrect_count)`, never stored — so it's
never stale and never fabricated ahead of having both counts.

### `ai_interactions` (Phase 6)

Managed by `app/repositories/ai_interaction_repository.py`. A lightweight
usage log, not a copy of personal data — see [AI.md](AI.md)'s Privacy
section. Written only after a successful `/api/ai/explain/*` call; failed
calls aren't logged.

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `user_id` | string | indexed |
| `interaction_type` | string | `grammar_explanation` \| `vocabulary_explanation` \| `mistake_explanation` (Phase 6); `vocabulary_question_generation` \| `grammar_question_generation` \| `mini_story_generation` (Phase 7) |
| `concept` | string | the term/concept asked about (or generated) — not the full prompt or Gemini's response |
| `created_at` | datetime (UTC) | |

### `mini_stories` (Phase 7)

Managed by `app/repositories/mini_story_repository.py`. One document per
generated story. Unlike `questions`, a story's comprehension questions are
embedded directly (they're only ever meaningful in the context of their
own story, not reusable across other content the way a vocabulary/grammar
question is).

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `title` | string | |
| `level` | string | `JLPTLevel` value |
| `story` | string | original AI-generated Japanese text, 20–2000 chars |
| `translation` | string | English translation |
| `vocab_highlights` | string[] | 1–15 notable words/phrases from the story |
| `comprehension_questions` | array | each: `prompt`, `options` (4, unique), `correct_answer`, `explanation` — `correct_answer`/`explanation` never returned by `GET`-equivalent responses, only revealed per-answer after submitting |
| `generated_by_user_id` | string | indexed; who requested it — also the ownership check for submitting answers (a non-owner gets 404, not 403) |
| `created_at` | datetime (UTC) | |

Note: `questions` (Phase 4) gained a `source` field in Phase 7 —
`"ai_generated"` for content created via `/api/ai/generate/*`, absent
(not `"seed"`) for the original Phase 4 seed data. This lets tests (and any
future cleanup/reporting) distinguish the two without touching existing
seeded documents.

### `conversation_sessions` (Phase 8)

Managed by `app/repositories/conversation_repository.py::ConversationSessionRepository`.
One document per started roleplay conversation. `scenario_key`/`character_key`
are static lookups into `app/core/conversation_data.py`, not denormalized
copies — a scenario's character/title/etc. can never drift out of sync with
what's actually shown, since there's only one place they're defined.

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `user_id` | string | indexed |
| `scenario_key` | string | `ramen_shop` \| `convenience_store` \| `train_station` |
| `character_key` | string | derived from the scenario at start time |
| `level` | string | `JLPTLevel` value chosen when starting |
| `started_at` | datetime (UTC) | |
| `last_message_at` | datetime (UTC) | updated by `touch()` after each successful exchange — powers "newest first" ordering in the history list |
| `message_count` | int | incremented by `touch()`; only counts messages from a successful exchange (see `conversation_messages` note below) |

### `conversation_messages` (Phase 8)

Managed by `app/repositories/conversation_repository.py::ConversationMessageRepository`.
One document per turn (`role: "user"` or `"character"`), ordered by
`created_at` and replayed (bounded by `HISTORY_LIMIT = 20`) into every
Gemini prompt so the character/scene stay consistent across turns despite
each Gemini call being stateless. The opening `"character"` message per
session is a static, curated line from `conversation_data.py` (not
AI-generated) — guarantees a consistent first line and saves a Gemini call.

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `session_id` | string | indexed |
| `role` | string | `user` \| `character` |
| `content` | string | Japanese text |
| `translation` | string \| null | English translation; `null` for user messages (never translated) |
| `created_at` | datetime (UTC) | |

**Important:** `ConversationService.send_message` calls `AIService.continue_conversation`
*before* persisting the user's message — if Gemini fails, nothing is written
for that turn. Persisting the user's turn first (attempted, then reverted
in review) would leave a dangling "user" message with no reply, which would
then be replayed as history into the *next* prompt and confuse the
character about whose turn it is.

Deliberately **not** written to `learner_skills` — conversation is
open-ended, so there's no single "correct answer" per turn to score
correct/incorrect against; fabricating a mastery number for the
`conversation` category would violate the never-fabricate principle used
everywhere else in the learner model (see [DATABASE.md](DATABASE.md)'s
`learner_skills` section). Conversation activity is tracked instead via
these two collections and their own history view — `GET /api/progress`'s
`conversation` skill continues to report `has_data: false` until a later
phase gives it a real scoring mechanism.

### `speaking_attempts` (Phase 9)

Managed by `app/repositories/speaking_repository.py::SpeakingAttemptRepository`.
One document per pronunciation attempt. `prompt_key` is a static lookup
into `app/core/speaking_data.py` — the target phrase itself is denormalized
onto the document (`target_text`) so history stays meaningful even if a
future phase edits or removes a prompt.

| Field | Type | Notes |
|---|---|---|
| `_id` | ObjectId | |
| `user_id` | string | indexed |
| `prompt_key` | string | key into `app/core/speaking_data.py::SPEAKING_PROMPTS` |
| `level` | string | `JLPTLevel` value, copied from the prompt |
| `target_text` | string | the phrase the learner was asked to say |
| `transcript` | string | what the speech provider heard |
| `correct` | bool | `similarity >= 0.8` after normalizing whitespace/punctuation |
| `similarity` | float | 0–1, `difflib.SequenceMatcher` ratio between normalized target and transcript |
| `xp_earned` | int | 10 if `correct`, else 0 |
| `created_at` | datetime (UTC) | |

**Important:** `SpeakingService.submit_attempt` calls
`SpeechToTextService.transcribe` *before* creating this document — same
ordering lesson as Phase 8's `conversation_messages` (see above): a failed
transcription leaves no trace, rather than a dangling attempt with no
transcript.

## Planned Collections

These will be introduced as the relevant phase implements them:

```
kanji
progress_events
achievements
user_achievements
recommendations
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
learner_skills.(user_id, category, concept) (unique), learner_skills.user_id — implemented, see LearnerSkillRepository.ensure_indexes()
ai_interactions.user_id — implemented, see AIInteractionRepository.ensure_indexes()
mini_stories.level, mini_stories.generated_by_user_id — implemented, see MiniStoryRepository.ensure_indexes()
conversation_sessions.user_id — implemented, see ConversationSessionRepository.ensure_indexes()
conversation_messages.session_id — implemented, see ConversationMessageRepository.ensure_indexes()
speaking_attempts.user_id — implemented, see SpeakingAttemptRepository.ensure_indexes()
```

### Planned (minimum)

```
progress_events.userId
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
