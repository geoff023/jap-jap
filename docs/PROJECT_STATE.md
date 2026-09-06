# JapJap Project State

## Current Phase

Phase 3 — Core Learning (complete)

## Completed

- Phase 0: Open-source foundation, dev environment, CI/CD, testing infrastructure, docs.
- Phase 1: Authentication — registration, login, logout, JWT, protected routes, auth state.
- Phase 2: Onboarding — learning goals, experience, preferred level, JLPT target, editable profile, unrestricted level changes.
- Phase 3: Core Learning — vocabulary, grammar, flashcards, multiple choice, sentence completion, XP.

## Frontend

- React + TypeScript + Vite (`frontend/`), Tailwind CSS v4, React Router,
  TanStack Query, Zustand (auth only).
- New pages: `FlashcardsPage` (category toggle, flip-and-self-assess deck,
  submits review results for XP), `QuizPage` (category toggle, one
  multiple-choice/sentence-completion question at a time, submits all
  answers together for server-side scoring).
- `DashboardPage` now shows an XP badge and links to Flashcards/Quiz.
- `src/services/activityApi.ts`, `src/types/activity.ts`.
- Level is currently hardcoded to `N5` in both practice pages (only N5
  content is seeded so far — a level picker isn't useful yet; add one in
  Phase 13 alongside broader content).
- Test tooling: Vitest + RTL, 16 tests total (added `FlashcardsPage.test.tsx`,
  `QuizPage.test.tsx`).
- No JLPT test engine, AI, or STT yet — by design.

## Backend

- `app/core/seed_data.py` — `VOCABULARY_N5` (12 words), `GRAMMAR_N5` (8
  particle/conjugation points), original content, seeded into MongoDB at
  app startup if the collection is empty.
- `app/repositories/vocabulary_repository.py`, `grammar_repository.py`,
  `activity_repository.py` (learning_activities, append-only).
- `app/services/activity_service.py` — quiz generation (random item + 3
  distractors from the same level/category pool, 4 options, shuffled;
  correct answer never sent to the client) and scoring (recomputed
  server-side from stored content, never trusts a client-supplied
  "correct" flag); flashcard completion (self-assessed, lower XP).
  `NotEnoughContentError` (400) and `ProfileRequiredError` (404, onboarding
  required before any XP-earning endpoint accepts requests).
- `app/api/vocabulary.py`, `grammar.py` (`GET`, optional `?level=`),
  `activities.py` (`GET /quiz`, `POST /quiz/submit`,
  `POST /flashcards/complete`).
- `LearnerProfileRepository.upsert()` now takes an optional `set_on_insert`
  dict so `xp: 0` is only set on first profile creation — redoing onboarding
  never resets XP already earned. `increment_xp()` never upserts (a missing
  profile is a caller bug, not something to silently paper over).
- Test tooling: pytest, 37 tests total (added `test_activities.py`: content
  listing/auth, quiz option-count/shape, scoring correctness, XP
  accumulation across multiple submissions, onboarding-required gating on
  both quiz submit and flashcard completion).

## Database

- Added `vocabulary` (indexed on `level`), `grammar_concepts` (indexed on
  `level`), `learning_activities` (indexed on `user_id`, append-only).
  `learner_profiles` gained an `xp` field. See [DATABASE.md](DATABASE.md).
- Tests seed `vocabulary`/`grammar_concepts` explicitly via a `seed_content`
  fixture (httpx's `ASGITransport` doesn't run FastAPI lifespan events, so
  the app's own startup seeding never executes under test) — these two
  collections are deliberately *not* cleared between tests (shared
  reference content), unlike `users`/`learner_profiles`/`learning_activities`.

## AI

- Not implemented. Unchanged — see [AI.md](AI.md).

## Speech

- Not implemented. Unchanged.

## Testing

- Backend: pytest, 37 tests passing (health, config, auth, profile,
  activities/content/XP).
- Frontend: Vitest + React Testing Library, 16 tests passing.
- E2E (Playwright or similar): not yet set up — planned for a later phase.

## CI/CD

- Unchanged from Phase 1/2. Backend tests still run against a `mongo:7`
  service container in CI; content seeding happens via the same
  `seed_content` fixture used locally, no special CI-only handling needed.

## Known Issues

- None currently tracked.

## Technical Debt

- Carried over from Phase 1/2: `POST /api/auth/logout` is a protected no-op;
  no rate limiting on `/api/auth/*` or `/api/onboarding`.
- Only N5 content exists (12 vocabulary words, 8 grammar points) — enough to
  exercise the activity engine, not a real study library yet (Phase 13).
- No level picker in the practice UI yet (hardcoded to N5) since there's
  nothing else to pick.

## Important Decisions

- The git repository root is `jap-jap/` nested one level inside the
  `self-project/jap-jap/` folder on disk (pre-existing `git init` + GitHub
  remote `geoff023/jap-jap` were preserved rather than re-initialized).
- Quiz scoring is entirely server-side and stateless: `GET /quiz` never
  reveals the correct answer, and `POST /quiz/submit` recomputes correctness
  by re-fetching the referenced vocabulary/grammar documents by id — it
  never trusts a "correct" flag from the client. No quiz-session document is
  persisted between generate and submit; per section 46 of the spec,
  deterministic scoring stays in backend logic, not AI, and here not even
  client-trusted state.
- Vocabulary quizzes are labeled `multiple_choice`; grammar quizzes are
  labeled `sentence_completion` — same underlying quiz engine
  (`ActivityService.generate_quiz`/`submit_quiz`), differing only in which
  content fields are used as prompt/answer. This satisfies both activity
  types from the master spec without duplicating logic.
- Flashcards are self-assessed (learner marks "know it" / "still learning")
  and earn less XP per item (5) than a verified quiz answer (10) — the
  difference is deliberate: one is graded by the server, the other isn't.
- XP-earning endpoints (`quiz/submit`, `flashcards/complete`) require a
  completed onboarding (404 otherwise) so `increment_xp` never has to decide
  whether to create a bogus, field-incomplete profile document.
- `xp` is set via `$setOnInsert` at onboarding time and only ever
  incremented afterward — resubmitting onboarding (a supported, idempotent
  action per Phase 2) cannot reset XP a learner already earned.

## Next Phase

Phase 4 — Test Engine (test creation, questions, attempts, scoring, result
page, history; vocabulary/grammar/mixed tests; connect results to learner
skills)
