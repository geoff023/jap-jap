# JapJap Project State

## Current Phase

Phase 4 — Test Engine (complete)

## Completed

- Phase 0: Open-source foundation, dev environment, CI/CD, testing infrastructure, docs.
- Phase 1: Authentication — registration, login, logout, JWT, protected routes, auth state.
- Phase 2: Onboarding — learning goals, experience, preferred level, JLPT target, editable profile, unrestricted level changes.
- Phase 3: Core Learning — vocabulary, grammar, flashcards, multiple choice, sentence completion, XP.
- Phase 4: Test Engine — test creation, questions, attempts, scoring, result page, history.

## Frontend

- React + TypeScript + Vite (`frontend/`), Tailwind CSS v4, React Router,
  TanStack Query, Zustand (auth only).
- New pages: `TestsPage` (list of the 3 seeded tests), `TestTakingPage`
  (one question at a time, submits all answers together — same pattern as
  `QuizPage`), `TestResultPage` (score + per-answer correct/incorrect +
  explanation), `TestHistoryPage` (past attempts, links to each result).
- New routes: `/tests`, `/tests/:testId`, `/tests/results/:attemptId`,
  `/tests/history` (all protected). Dashboard now has a third tile ("Tests")
  alongside Flashcards/Quiz.
- `src/services/testApi.ts`, `src/types/test.ts`.
- Test tooling: Vitest + RTL, 21 tests total (added `TestsPage.test.tsx`,
  `TestTakingPage.test.tsx`, `TestResultPage.test.tsx`,
  `TestHistoryPage.test.tsx`).
- No learner-skill dashboard, AI, or STT yet — by design.

## Backend

- `app/core/test_seed_data.py` — derives `Question` documents deterministically
  from the existing `VOCABULARY_N5`/`GRAMMAR_N5` (one source of truth for N5
  content, not a second authored question bank), then groups them into 3
  seeded `Test` documents: "N5 Vocabulary Test", "N5 Grammar Test", "N5
  Mixed Test". `seed_test_engine()` seeds questions first, then looks up
  their ids fresh by category to build tests — correct whether questions
  were just inserted or already existed.
- `app/repositories/question_repository.py`, `test_repository.py`,
  `test_attempt_repository.py` (test_attempts is the history/result-page
  data source directly — no separate `learning_activities` entry is written
  for test attempts).
- `app/services/test_service.py` — `get_test_detail` (never exposes
  `correct_answer`), `submit_attempt` (re-fetches questions by id and
  recomputes correctness server-side — a client's `selected` value is
  scored, never trusted as pre-scored; requires a completed profile, same
  `ProfileRequiredError` pattern as Phase 3), `get_attempt` (ownership-checked:
  a `test_attempt` belonging to another user returns 404, not 403 — never
  confirms whether an id exists to a non-owner).
- `app/api/tests.py` — `GET /api/tests`, `GET /api/tests/{id}`,
  `POST /api/tests/{id}/attempts`, `GET /api/tests/attempts`,
  `GET /api/tests/attempts/{id}`. Route registration order matters here:
  literal paths (`/attempts`, `/attempts/{id}`) are registered before the
  wildcard `/{test_id}`, or a request to `/attempts` would be matched as
  `test_id="attempts"`.
- Test tooling: pytest, 48 tests total (added `test_test_engine.py`: seeded
  content shape, hidden-answer contract on the detail endpoint, scoring,
  onboarding-required gating, unknown-id 404s, history listing, and
  cross-user ownership on attempt detail).

## Database

- Added `questions` (indexed on `category`, `level`), `tests` (indexed on
  `category`, `level`), `test_attempts` (indexed on `user_id`, append-only —
  this *is* the test history/result data, holding a full answer breakdown
  per attempt). See [DATABASE.md](DATABASE.md).
- Tests seed `questions`/`tests` via a new `seed_tests` fixture (same
  ASGITransport-doesn't-run-lifespan reason as Phase 3's `seed_content`);
  these two collections aren't cleared between tests (shared reference
  content), but `test_attempts` is.

## AI

- Not implemented. Unchanged — see [AI.md](AI.md).

## Speech

- Not implemented. Unchanged.

## Testing

- Backend: pytest, 48 tests passing (health, config, auth, profile,
  activities, test engine).
- Frontend: Vitest + React Testing Library, 21 tests passing.
- E2E (Playwright or similar): not yet set up — planned for a later phase.

## CI/CD

- Unchanged from Phase 1–3. Backend tests still run against a `mongo:7`
  service container in CI.

## Known Issues

- None currently tracked.

## Technical Debt

- Carried over: `POST /api/auth/logout` protected no-op; no rate limiting on
  auth/onboarding; only N5 content exists (12 vocab words, 8 grammar
  points → 20 questions across 3 tests); no level picker in the UI yet.
- Tests are seeded system-side, not user-authored — there's no
  test-creation UI. Acceptable for now (matches "start with vocabulary,
  grammar, mixed tests" in the master spec); an authoring flow isn't
  currently planned as a named phase.
- `test_attempts.answers[].concept` is stored but nothing yet *reads* it
  in aggregate — that's explicitly Phase 5's job (learner model / skill
  mastery), not implied to be missing here.

## Important Decisions

- The git repository root is `jap-jap/` nested one level inside the
  `self-project/jap-jap/` folder on disk (pre-existing `git init` + GitHub
  remote `geoff023/jap-jap` were preserved rather than re-initialized).
- Test Engine content (`questions`, `tests`) is derived from Phase 3's
  vocabulary/grammar seed data rather than authored a second time — one
  source of truth for N5 content. Question distractors are chosen by a
  fixed index-rotation scheme (not random), so seeded content — and which
  options appear per question — is stable and reproducible across restarts
  and test runs, unlike Phase 3's per-request random quiz distractors
  (a deliberate difference: quiz content there is regenerated fresh on every
  request, test content here must stay fixed since a `test_attempt`
  references specific `question_id`s that must keep meaning the same thing).
- `questions` are standalone/reusable, referenced by `tests.question_ids`
  rather than embedded per-test — this is what makes the "mixed" test
  possible without duplicating vocabulary/grammar questions into a third copy.
- Test scoring, like Phase 3's quiz, is entirely server-side: the client
  never receives `correct_answer` before submitting, and submission
  recomputes correctness from the stored question rather than trusting
  anything the client claims about its own answer.
- `test_attempts` is deliberately its own collection rather than reusing
  `learning_activities` — a test attempt carries a richer, fixed shape (full
  per-question answer breakdown for the result page) that the lighter
  Phase 3 activity log was never meant to hold.
- An attempt lookup by a non-owning user returns `404`, matching the
  established pattern (Phase 2/3 also return 404 rather than 403 for
  "doesn't exist for you") so the endpoint never leaks whether an id exists.

## Next Phase

Phase 5 — Learner Model + Progress (skill mastery, progress dashboard,
mistakes, activity history, estimated JLPT readiness — never fabricated)
