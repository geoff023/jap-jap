# JapJap Project State

## Current Phase

Phase 8 — Text Conversation (complete)

## Completed

- Phase 0: Open-source foundation, dev environment, CI/CD, testing infrastructure, docs.
- Phase 1: Authentication — registration, login, logout, JWT, protected routes, auth state.
- Phase 2: Onboarding — learning goals, experience, preferred level, JLPT target, editable profile, unrestricted level changes.
- Phase 3: Core Learning — vocabulary, grammar, flashcards, multiple choice, sentence completion, XP.
- Phase 4: Test Engine — test creation, questions, attempts, scoring, result page, history.
- Phase 5: Learner Model + Progress — skill mastery, progress dashboard, mistakes, activity history, estimated JLPT readiness.
- Phase 6: Gemini AI Tutor — AIService → GeminiService, grammar/vocabulary/mistake explanations, structured + Pydantic-validated, mocked in all tests.
- Phase 7: AI Content Generation — supplementary AI-generated vocabulary/grammar questions, mini stories, comprehension questions; all validated and stored.
- Phase 8: Text Conversation — roleplay conversation sessions with AI characters across 3 scenarios (ramen shop, convenience store, train station), full history threading for scenario consistency, conversation history view.

## Frontend

- React + TypeScript + Vite (`frontend/`), Tailwind CSS v4, React Router,
  TanStack Query, Zustand (auth only).
- `src/services/aiGenerationApi.ts`, `src/types/aiGeneration.ts` — client
  for the five new `/api/ai/generate/*` and `/api/ai/generated-questions/*`
  and `/api/ai/mini-stories/*` endpoints.
- New pages: `AIPracticePage` (`/ai-practice` — pick category + any JLPT
  level N5–N1, generate a single question on demand, answer it, get scored;
  unlike other practice pages this one lets the learner pick *any* level
  since generation doesn't depend on pre-seeded content) and
  `MiniStoriesPage` (`/mini-stories` — pick a level and optional topic,
  generate a story with reading comprehension questions answered one form,
  submitted together).
- Dashboard's practice grid grew to 6 tiles (3×2): Flashcards, Quiz, Tests,
  Progress, AI Practice, Mini Stories.
- Test tooling: Vitest + RTL, 34 tests total (added
  `AIPracticePage.test.tsx`, `MiniStoriesPage.test.tsx`).

### Phase 8 additions

- `src/services/conversationApi.ts`, `src/types/conversation.ts` — client
  for the five `/api/conversation/*` endpoints.
- New pages: `ConversationScenariosPage` (`/conversation` — pick a JLPT
  level and one of 3 scenarios, starts a session and navigates to it),
  `ConversationChatPage` (`/conversation/:sessionId` — chat-bubble UI,
  send a message, see the character's reply and translation, XP earned),
  `ConversationHistoryPage` (`/conversation/history` — past sessions,
  newest-activity-first, links back into each one).
- Dashboard's practice grid grew to 7 tiles: added Conversation (💬).
- Test tooling: Vitest + RTL, 41 tests total (added
  `ConversationScenariosPage.test.tsx`, `ConversationChatPage.test.tsx`,
  `ConversationHistoryPage.test.tsx`).

## Backend

- `app/schemas/ai_generation.py` — `GeneratedQuestion` and
  `GeneratedMiniStory` (with nested `ComprehensionQuestion`s), each with a
  `model_validator` enforcing the *business* rules Pydantic's field types
  alone can't (`_validate_multiple_choice`: exactly 4 unique options, the
  correct answer among them) — this is the "business validation" step in
  the Gemini → structured output → Pydantic validation → business
  validation → database pipeline from [AI.md](AI.md), not skippable
  shape-checking.
- `app/ai/base.py` / `gemini_service.py` — three new `AIService` methods:
  `generate_vocabulary_question`, `generate_grammar_question`,
  `generate_mini_story` (the last generates the story *and* its
  comprehension questions in one Gemini call — cheaper, and keeps questions
  grounded in the actual story text).
- `app/services/content_generation_service.py::ContentGenerationService` —
  orchestrates generation → storage → `ai_interactions` logging, and
  scoring (`submit_generated_question`, `submit_comprehension`) using the
  same deterministic re-check-against-stored-content pattern as Phases 3–4
  (Gemini is never asked to grade an answer).
- `app/api/ai_generation.py` — `POST /api/ai/generate/{vocabulary,grammar}-question`,
  `POST /api/ai/generate/mini-story`,
  `POST /api/ai/generated-questions/{id}/submit`,
  `POST /api/ai/mini-stories/{id}/comprehension/submit`. Generation itself
  needs no onboarding (browsing/generating content is free, like
  `GET /api/vocabulary`); only submitting an answer (which earns XP)
  requires it, and only submitting a mini-story's comprehension additionally
  enforces ownership (404, not 403, for someone else's story — same pattern
  as Phase 4's test attempts).
- Generated vocabulary/grammar questions are stored in the *existing*
  `questions` collection (Phase 4), tagged `source: "ai_generated"` — no new
  collection needed, and they're structurally reusable by a future Test if
  a later phase wants that. Mini stories get their own `mini_stories`
  collection since their comprehension questions are story-specific, not
  reusable content.
- **Comprehension answers now feed the `reading` category in the learner
  model** — the first real data source for `reading` since Phase 5
  introduced the category with permanently `has_data: false`.
- Test tooling: pytest, 93 tests total (added `test_ai_generation.py`:
  generation stores content and hides the answer, both submit endpoints
  score correctly and award/withhold XP correctly, ownership enforcement on
  mini-story submission, `reading`/`vocabulary` skill feed-through, and the
  same 502/503 patterns as Phase 6; extended `test_gemini_service.py` with
  business-validation-rejection cases: too few options, duplicate options,
  correct answer missing from options).

### Phase 8 additions

- `app/core/conversation_data.py` — static roster of characters and
  scenarios (see [AI.md](AI.md)); `app/schemas/conversation.py` — request/
  response schemas plus `ConversationReply` (Gemini's per-turn structured
  output).
- `app/ai/base.py` / `gemini_service.py` — new `continue_conversation`
  method: builds a prompt from the character's personality, the scenario,
  the learner's JLPT level, and the full replayed history, then validates
  Gemini's JSON reply the same way as every other `AIService` method.
- `app/repositories/conversation_repository.py` —
  `ConversationSessionRepository` / `ConversationMessageRepository`.
- `app/services/conversation_service.py::ConversationService` — starts
  sessions (static opening line, no Gemini call), sends messages
  (reconstructs history → calls Gemini → persists both turns → awards
  XP), lists/fetches sessions with ownership checks. Persists the
  learner's message only *after* the AI reply succeeds — see
  [DATABASE.md](DATABASE.md) for why persisting it first would corrupt
  future history.
- `app/api/conversation.py` — `GET /api/conversation/scenarios`,
  `POST /api/conversation/sessions`, `GET /api/conversation/sessions`,
  `GET /api/conversation/sessions/{id}`,
  `POST /api/conversation/sessions/{id}/messages`. Scenario/session
  browsing needs no onboarding; starting a session and sending a message
  do (XP-earning), matching the established pattern.
- 3 XP per message sent — lower than quiz/test XP (10) since there's no
  correct/incorrect answer to verify; conversation is deliberately **not**
  written to `learner_skills` (see [AI.md](AI.md)'s "What Gemini Is (and
  Isn't) Used For").
- Test tooling: pytest, 108 tests total (added `test_conversation.py`:
  scenario listing, session start/opening-line correctness, message
  send + XP award, per-scenario character correctness, **history
  accumulation across turns** — the scenario-consistency test — ownership
  checks, and the 404/502 error paths).

## Database

- Added `mini_stories` (indexed on `level`, `generated_by_user_id`).
  `questions` (Phase 4) gained an optional `source` field
  (`"ai_generated"` vs absent-for-seeded) — no schema migration needed since
  MongoDB is schemaless and existing seeded documents are simply treated as
  "not AI-generated" by omission. See [DATABASE.md](DATABASE.md).
- Tests clean `mini_stories` fully and `questions` filtered to
  `source: "ai_generated"` between tests (seeded questions stay, matching
  the existing shared-reference-content pattern).
- Added `conversation_sessions` (indexed on `user_id`) and
  `conversation_messages` (indexed on `session_id`). Tests clean both
  fully between runs. See [DATABASE.md](DATABASE.md).

## AI

- Extended — see [AI.md](AI.md) for the full Phase 6–8 pipeline, storage
  design, conversation-consistency approach, and privacy notes.

## Speech

- Not implemented. Unchanged.

## Testing

- Backend: pytest, 108 tests passing (health, config, auth, profile,
  activities, test engine, learner model/progress, AI tutor, AI content
  generation, conversation).
- Frontend: Vitest + React Testing Library, 41 tests passing.
- E2E (Playwright or similar): not yet set up — planned for a later phase.
- **Manually verified against the real Gemini API** (same non-functional
  local key as Phases 6–7): registered a user, completed onboarding,
  started a Ramen Shop conversation with Momo (confirmed the correct
  static opening line and character), and sent a message — confirmed the
  request genuinely reaches Gemini (visible in the backend log as a real
  502 from the provider, not an instant mock response) and the learner
  sees the same friendly retry message pattern established in Phase 6.
  This manual run also caught a real bug — the learner's message was being
  persisted *before* the Gemini call, so a failed reply left a dangling,
  unanswered turn in the database that would have corrupted the next
  prompt's history — fixed by reordering `ConversationService.send_message`
  to persist only after the reply succeeds (verified in the same manual
  session: a second failed send left the message count unchanged).

## CI/CD

- Unchanged from Phase 1–6. Backend tests still run against a `mongo:7`
  service container in CI. No `GEMINI_API_KEY` is set or required in CI —
  every AI-dependent test uses `FakeAIService`.

## Known Issues

- None currently tracked.

## Technical Debt

- Carried over: `POST /api/auth/logout` protected no-op; no rate limiting on
  auth/onboarding/AI endpoints (every message sent in a conversation is now
  its own Gemini call, on top of the Phase 7 generate/submit calls — rate
  limiting AI endpoints specifically should be a priority before any public
  deployment); only N5 seed content exists (AI generation partially offsets
  this by supporting any JLPT level on demand); no level picker on the
  *seeded*-content practice pages.
- AI-generated questions are stored indefinitely with no expiry/cleanup —
  fine at current scale, worth revisiting if generation volume grows.
- `mini_stories` documents are never listed back to their creator (no
  "my past stories" page) — each generation is a one-off experience, by
  design for this phase; revisit if that turns out to feel incomplete.
- Conversation sessions never expire/archive and `HISTORY_LIMIT` (20) is a
  fixed constant, not configurable per level/scenario — fine at current
  scale; a very long-running session's early turns simply drop out of what
  gets replayed to Gemini, which only matters if a learner has an
  unusually long single conversation.
- No way to end/delete a conversation session — sessions accumulate
  indefinitely in the history list; acceptable for now since browsing is
  free and there's no per-session cost beyond storage.

## Important Decisions

- The git repository root is `jap-jap/` nested one level inside the
  `self-project/jap-jap/` folder on disk (pre-existing `git init` + GitHub
  remote `geoff023/jap-jap` were preserved rather than re-initialized).
- Generated vocabulary/grammar questions reuse Phase 4's `questions`
  collection rather than getting their own — they're structurally identical
  content (prompt/options/correct_answer/explanation/concept/category/level),
  and a `source` tag is enough to distinguish provenance without a schema
  fork. Mini stories get a dedicated collection because their comprehension
  questions are embedded and story-specific, not a reusable unit the way a
  vocabulary/grammar question is.
- `_validate_multiple_choice` lives as a `model_validator` on the Pydantic
  schemas themselves (`app/schemas/ai_generation.py`), not as separate
  "business validation" code called after Pydantic — for this app, the
  business rules (4 unique options, correct answer present) are simple and
  static enough that keeping them co-located with the schema is clearer
  than a second validation pass, while still being conceptually the
  pipeline's distinct "business validation" step.
- Comprehension question answers write to `learner_skills` with
  `category: "reading"` and `concept: <story title>` — a deliberate choice
  to give `reading` its first real data source now rather than waiting for
  a dedicated reading-comprehension phase, since Phase 7's mini stories are
  functionally exactly that.
- Standalone generated questions (unlike quiz/test answers) award 0 XP for
  a wrong answer rather than some smaller deterministic penalty — matches
  the quiz/test XP model (Phase 3/4) exactly: correct answers earn XP,
  incorrect answers earn none, never negative.
- Generation endpoints (`/generate/*`) don't require completed onboarding;
  only the endpoints that award XP (`*/submit`) do — matches the existing
  "browsing is free, earning XP requires a profile" pattern from Phases 3–4
  (e.g. `GET /api/vocabulary` vs `POST /api/activities/quiz/submit`).
- Characters and scenarios (Phase 8) are a static, in-code roster
  (`app/core/conversation_data.py`), not a database collection — small and
  curated enough that versioning them alongside the app guarantees "which
  character speaks in which scenario" can never drift, unlike a database
  record that could be edited independently of the code that assumes its
  shape.
- Scenario opening lines are static/curated, not AI-generated — guarantees
  a consistent first line from turn 0 for every learner in a given
  scenario, and saves one Gemini call per session start.
- `ConversationService.send_message` calls Gemini *before* persisting the
  learner's message (not the other way around) — discovered via manual
  browser verification that persisting first would leave a dangling,
  unanswered user turn in the database on AI failure, corrupting the next
  prompt's history reconstruction. This ordering also means a failed send
  costs nothing in stored state — a retry is indistinguishable from a first
  attempt.
- Conversation turns intentionally do **not** feed `learner_skills` — open-
  ended chat has no single correct answer to score against, so recording it
  would mean fabricating a mastery number, violating the never-fabricate
  principle used everywhere else in the learner model. XP is a flat 3 per
  message instead of a correctness-based amount.
- Conversation XP (3/message) is deliberately lower than quiz/test XP
  (10/correct answer) since sending a message requires no correctness check
  — keeps the XP economy weighted toward verified learning, not just
  activity volume.

## Next Phase

Phase 9 — Speech-to-Text (pronunciation practice, `SpeechToTextService`
abstraction mirroring `AIService`, speaking attempts, integration with the
`speaking` learner-model category)
