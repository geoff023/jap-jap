# AI

**Status: implemented (Phases 6–8).** Grammar/vocabulary/mistake
explanations (Phase 6), supplementary content generation — vocabulary
questions, grammar questions, mini stories with reading comprehension
(Phase 7) — and character roleplay conversation (Phase 8) via Gemini,
behind an `AIService` abstraction. Personalized feedback remains for later
phases (10+). Speech-to-Text is still unimplemented — see the bottom of
this doc.

## Provider

JapJap uses the [Google Gemini API](https://ai.google.dev/) (`google-genai`
SDK, model `gemini-2.0-flash` by default) for AI features.
Each contributor supplies their own API key locally — no key is ever
committed to the repository, checked into CI, or shared by the project.

## Abstraction

```
AIService (app/ai/base.py)
    ↓
GeminiService (app/ai/gemini_service.py)
```

Application code depends on the `AIService` interface, not on the Gemini SDK
directly — `app/api/ai.py`'s routes and dependency injection
(`app/api/deps.py::get_ai_service`) never import `google.genai`. This keeps
Gemini calls out of routes/services scattered across the codebase and makes
the provider swappable (a second implementation would just be another
`AIService` subclass).

`AIService` currently defines seven methods: `explain_grammar`,
`explain_vocabulary`, `explain_mistake` (Phase 6);
`generate_vocabulary_question`, `generate_grammar_question`,
`generate_mini_story` (Phase 7, in `app/schemas/ai_generation.py`'s
`GeneratedQuestion`/`GeneratedMiniStory` return types); and
`continue_conversation` (Phase 8, returning `ConversationReply` from
`app/schemas/conversation.py`).
`app/services/content_generation_service.py::ContentGenerationService`
orchestrates the Phase 7 generation methods: call `AIService` → persist the
already-validated result → log the interaction, keeping that
storage/logging concern out of `GeminiService` itself (which only knows
about talking to Gemini). `app/services/conversation_service.py::ConversationService`
plays the analogous role for Phase 8: reconstruct history → call
`continue_conversation` → persist both turns → award XP.

## Data Flow

```
Gemini → structured output → Pydantic validation → business validation → database
```

AI responses are **untrusted generated data**. Concretely, `GeminiService`:

1. Builds a prompt that spells out the exact JSON shape needed and requests
   `response_mime_type="application/json"`.
2. Parses the response text as JSON (`json.JSONDecodeError` → `AIServiceError`).
3. Validates the parsed dict against our own Pydantic schema
   (`GrammarExplanation` / `VocabularyExplanation` / `MistakeExplanation` in
   `app/schemas/ai.py`) — a `ValidationError` also becomes an
   `AIServiceError`, never an unhandled crash or unvalidated data reaching
   a route.

Deliberately, `GeminiService` does **not** rely on the SDK's own
schema-binding/auto-parse feature (`response_schema` + `response.parsed`) as
the source of truth — our explicit Pydantic validation is what gates whether
a response is usable, so the validation step is easy to reason about and to
test independently of the SDK's behavior.

Gemini never writes to the database directly — only application code does,
and only after both `AIServiceError`-free validation above. For Phase 7's
generated content specifically, "business validation" (the step between
Pydantic validation and the database in the pipeline diagram above) lives
in the same Pydantic models as `model_validator` checks
(`app/schemas/ai_generation.py::_validate_multiple_choice`): a generated
question isn't just *shaped* like JSON with the right keys, it must also
have exactly 4 unique options with the correct answer among them, or the
whole response is rejected as an `AIServiceError` before anything is stored.

## What Gemini Is (and Isn't) Used For

**Used for (Phase 6):** grammar/vocabulary/mistake explanations.
**Used for (Phase 7):** supplementary content generation — vocabulary
questions, grammar questions, mini stories with reading comprehension
questions (all generated on demand, not pre-seeded).
**Used for (Phase 8):** in-character roleplay replies for conversation
practice — each reply is generated fresh per turn, grounded in the
character's persona, the scenario, the learner's JLPT level, and the full
conversation history so far.
**Used for (later phases):** personalized natural-language feedback,
semantic analysis.

**Not used for:** XP, scoring, progress arithmetic, authentication,
database operations, or deterministic ranking — those stay in backend
business logic (see Phases 3–5) so they're consistent, testable, and free
of AI cost/latency. Quiz/test scoring in particular is verified server-side
by re-checking the learner's answer against stored content — Gemini is
never asked whether an answer is "correct." This applies equally to Phase
7's generated content: once a question/story is stored, answering it is
scored the exact same deterministic way as seeded content (see
`ContentGenerationService.submit_generated_question` /
`submit_comprehension`) — Gemini is only ever asked to *create* content, never
to grade a learner's response to it. Phase 8's conversation is open-ended
by nature (there's no "correct" reply to a chat message), so it isn't
scored at all — XP is a flat per-message amount, not a correctness-based
one, and conversation turns are never written to `learner_skills` (would
require fabricating a mastery number with no real basis — see
[DATABASE.md](DATABASE.md)).

## Graceful Degradation

The application runs, and `/api/health` succeeds, with no `GEMINI_API_KEY`
set. `get_ai_service` (in `app/api/deps.py`) checks `Settings.ai_enabled`
and raises `503 Service Unavailable` with a clear message *before*
constructing a `GeminiService` — only the `/api/ai/explain/*` and
`/api/ai/generate/*` routes become unavailable, nothing else. If Gemini
itself fails or returns something invalid (`AIServiceError`), the route
returns `502 Bad Gateway` with a generic message — the underlying provider
error is logged server-side, never leaked to the client. Manually verified
against the real API in Phases 6–8 with a non-functional local key: the
request genuinely reaches Gemini, gets rejected, and the learner sees a
friendly retry message either way.

## Conversation Consistency (Phase 8)

Each call to `continue_conversation` is a stateless Gemini request — the
model has no memory of earlier turns unless the caller supplies it. Two
things keep a character and scenario consistent across a long conversation
despite that:

1. **Static opening lines.** The first message in every session
   (`app/core/conversation_data.py`'s `opening_line`/`opening_translation`)
   is curated, not generated — guarantees a consistent, on-character first
   line from turn 0, and saves a Gemini call per session start.
2. **Full history replay.** `ConversationService.send_message` fetches up
   to `HISTORY_LIMIT` (20) prior messages and threads them into every
   prompt as `"Learner: ..." / "<Character name>: ..."` lines, alongside
   the character's fixed personality description and the scenario's
   title/setting. This is what makes Momo stay Momo (casual, encouraging)
   and stay in the ramen shop scene ten messages in, rather than drifting.

The learner's message is persisted only *after* the character's reply
succeeds (see [DATABASE.md](DATABASE.md)'s `conversation_messages` note) —
storing it earlier and having the Gemini call fail would leave a
user-turn-with-no-reply in the history, which would then get replayed into
the *next* prompt and confuse the character about whose turn it is.

`tests/test_conversation.py` asserts this consistency directly: each
scenario is checked to invoke its own assigned character
(`fake_ai_service.calls`), and a multi-message exchange is checked to
accumulate history correctly turn-over-turn (1 message before the first
reply, 3 before the second, in the right role order).

## Testing

Automated tests never call the real Gemini API:

* `tests/fakes.py::FakeAIService` is a test double implementing `AIService`,
  swapped in per-test via `app.dependency_overrides[get_ai_service]` (see
  the `fake_ai_service` fixture in `tests/conftest.py`). Route tests
  (`tests/test_ai.py`) use this — auth, request validation, the 502 path
  (`should_fail=True`), the 503-without-a-key path (achieved by overriding
  `get_settings`, not by relying on the ambient environment — a developer's
  real local `.env` key must not make CI-equivalent tests non-deterministic),
  and that only successful calls are logged to `ai_interactions`.
* `tests/test_gemini_service.py` unit-tests `GeminiService` itself, with
  `genai.Client`'s one network-touching method
  (`client.aio.models.generate_content`) replaced by a mock — malformed
  JSON, missing required fields, an empty response, and a wrapped SDK
  exception are each asserted to raise `AIServiceError`; Phase 7 adds cases
  for the business-validation rules (too few options, a correct answer not
  present in the options, duplicate options).
* `tests/test_ai_generation.py` covers the Phase 7 routes with
  `fake_ai_service`: generated content is stored and returned without a
  correct answer, submitting a generated question/comprehension answer
  scores correctly and feeds the learner model (including `reading`, which
  had no other data source before Phase 7), ownership checks on mini
  stories, and the same 502/503 patterns as Phase 6.
* `tests/test_conversation.py` covers the Phase 8 routes with
  `fake_ai_service` (which gained a `continue_conversation` method):
  scenario listing, starting a session returns the correct static opening
  line and character, sending a message returns the AI reply and awards
  XP, the correct character is used per scenario, history accumulates
  correctly across multiple turns (the scenario-consistency test), session
  ownership (404 for someone else's session), and the 404/502 error paths.

## Privacy

* Only the minimum context needed for a given AI feature is sent to Gemini
  (a concept/term string and an optional short context string, or a level +
  optional topic for generation — never a learner's full profile or history).
* Learner data is not used to train any model.
* AI interactions are logged to `ai_interactions` (see
  [DATABASE.md](DATABASE.md)) as `{user_id, interaction_type, concept,
  created_at}` only — never the full prompt or Gemini's response — so this
  collection stays a lightweight usage log, not a second copy of personal
  data. Failed calls are not logged (nothing useful happened). Not shared
  with other users; excluded from public logs.
* Phase 7's generated content itself (questions in `questions`, stories in
  `mini_stories`) is stored in full — it's learning material to be reused,
  not a usage log — but it's *content Gemini produced*, not personal data
  about the learner who requested it, beyond the `generated_by_user_id`/
  ownership field needed to gate who can submit answers to a given story.
* Phase 8's conversation turns (`conversation_messages`) are the one
  exception to "only a lightweight log is stored" — the learner's own
  message text is stored in full, since it's needed to reconstruct history
  for future turns and to show the learner their own past conversations.
  Only the minimum scenario/character context (never the learner's
  profile, goals, or history from other features) is sent to Gemini per
  turn.

## Content Storage (Phase 7)

Generated vocabulary/grammar questions are stored in the same `questions`
collection Phase 4's Test Engine uses, tagged `"source": "ai_generated"`
(seeded content has no `source` field, so this tag alone disambiguates the
two without needing to touch existing documents). This means AI-generated
questions are structurally identical to seeded ones and could be pulled
into a future Test's `question_ids` — Phase 7 doesn't do that automatically,
but nothing would need to change in `questions`' shape if a later phase
wanted to. Mini stories get their own `mini_stories` collection (a story's
comprehension questions are naturally scoped to that one story, unlike
vocab/grammar questions which are meant to be reusable across many tests).

## Characters and Scenarios (Phase 8)

`app/core/conversation_data.py` defines a static roster of 5 characters
(only `momo`, `kiko`, `kenji` are assigned to a scenario yet — `yuki`/`ponta`
are pre-defined for later phases to pick up without re-designing the cast)
and 3 scenarios (`ramen_shop`, `convenience_store`, `train_station`), each
scenario permanently paired with one character. This lives in code, not the
database — small enough to version alongside the rest of the app, and it
guarantees "which character speaks in which scenario" can never drift out
of sync the way a database record edited independently of the code could.

## Configuration Bug Fixed in Phase 6

`Settings`' `env_file` paths were relative to the process's current working
directory, not to `backend/`. Running the app via `uvicorn --app-dir backend
app.main:app` from the repo root only adds `backend/` to `sys.path` — it
does not `chdir` there — so `.env` silently failed to load in that launch
style (discovered while manually verifying this phase with a real API key).
Fixed by resolving both candidate `.env` paths from `Path(__file__)` in
`app/core/config.py`, independent of CWD. `cd backend && uvicorn ...` (the
documented way to run the app) was unaffected either way.

## Speech-to-Text

Mirrors the AI abstraction:

```
SpeechToTextService
    ↓
STTProvider
```

Still unimplemented; see Phase 9 in [PROJECT_STATE.md](PROJECT_STATE.md).
