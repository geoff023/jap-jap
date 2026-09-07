# JapJap Project State

## Current Phase

Phase 7 — AI Content Generation (complete)

## Completed

- Phase 0: Open-source foundation, dev environment, CI/CD, testing infrastructure, docs.
- Phase 1: Authentication — registration, login, logout, JWT, protected routes, auth state.
- Phase 2: Onboarding — learning goals, experience, preferred level, JLPT target, editable profile, unrestricted level changes.
- Phase 3: Core Learning — vocabulary, grammar, flashcards, multiple choice, sentence completion, XP.
- Phase 4: Test Engine — test creation, questions, attempts, scoring, result page, history.
- Phase 5: Learner Model + Progress — skill mastery, progress dashboard, mistakes, activity history, estimated JLPT readiness.
- Phase 6: Gemini AI Tutor — AIService → GeminiService, grammar/vocabulary/mistake explanations, structured + Pydantic-validated, mocked in all tests.
- Phase 7: AI Content Generation — supplementary AI-generated vocabulary/grammar questions, mini stories, comprehension questions; all validated and stored.

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

## Database

- Added `mini_stories` (indexed on `level`, `generated_by_user_id`).
  `questions` (Phase 4) gained an optional `source` field
  (`"ai_generated"` vs absent-for-seeded) — no schema migration needed since
  MongoDB is schemaless and existing seeded documents are simply treated as
  "not AI-generated" by omission. See [DATABASE.md](DATABASE.md).
- Tests clean `mini_stories` fully and `questions` filtered to
  `source: "ai_generated"` between tests (seeded questions stay, matching
  the existing shared-reference-content pattern).

## AI

- Extended — see [AI.md](AI.md) for the full Phase 7 pipeline, storage
  design, and privacy notes.

## Speech

- Not implemented. Unchanged.

## Testing

- Backend: pytest, 93 tests passing (health, config, auth, profile,
  activities, test engine, learner model/progress, AI tutor, AI content
  generation).
- Frontend: Vitest + React Testing Library, 34 tests passing.
- E2E (Playwright or similar): not yet set up — planned for a later phase.
- **Manually verified against the real Gemini API** (same non-functional
  local key as Phase 6): confirmed `/api/ai/generate/vocabulary-question`
  genuinely reaches Gemini (visible in network requests as a real HTTP
  round-trip, not an instant mock response) and that a provider failure
  renders as the same friendly retry message pattern established in Phase 6.

## CI/CD

- Unchanged from Phase 1–6. Backend tests still run against a `mongo:7`
  service container in CI. No `GEMINI_API_KEY` is set or required in CI —
  every AI-dependent test uses `FakeAIService`.

## Known Issues

- None currently tracked.

## Technical Debt

- Carried over: `POST /api/auth/logout` protected no-op; no rate limiting on
  auth/onboarding/AI endpoints (generation endpoints are the most
  cost-bearing calls in the app now — two Gemini calls per learner action
  in the worst case, generate then submit — rate limiting these specifically
  should be a priority before any public deployment); only N5 seed content
  exists (AI generation partially offsets this by supporting any JLPT level
  on demand); no level picker on the *seeded*-content practice pages.
- AI-generated questions are stored indefinitely with no expiry/cleanup —
  fine at current scale, worth revisiting if generation volume grows.
- `mini_stories` documents are never listed back to their creator (no
  "my past stories" page) — each generation is a one-off experience, by
  design for this phase; revisit if that turns out to feel incomplete.

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

## Next Phase

Phase 8 — Text Conversation (conversation sessions, characters, scenarios,
Gemini responses, conversation history; starting with ramen shop,
convenience store, train station scenarios)
