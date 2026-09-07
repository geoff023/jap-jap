# JapJap Project State

## Current Phase

Phase 5 — Learner Model + Progress (complete)

## Completed

- Phase 0: Open-source foundation, dev environment, CI/CD, testing infrastructure, docs.
- Phase 1: Authentication — registration, login, logout, JWT, protected routes, auth state.
- Phase 2: Onboarding — learning goals, experience, preferred level, JLPT target, editable profile, unrestricted level changes.
- Phase 3: Core Learning — vocabulary, grammar, flashcards, multiple choice, sentence completion, XP.
- Phase 4: Test Engine — test creation, questions, attempts, scoring, result page, history.
- Phase 5: Learner Model + Progress — skill mastery, progress dashboard, mistakes, activity history, estimated JLPT readiness.

## Frontend

- React + TypeScript + Vite (`frontend/`), Tailwind CSS v4, React Router,
  TanStack Query, Zustand (auth only).
- New pages: `ProgressPage` (overall mastery, per-skill breakdown across all
  7 tracked categories, estimated JLPT readiness with an explicit
  "not an official JLPT prediction" disclaimer), `MistakesPage` (recurring
  wrong-answer concepts, most-missed first), `ActivityHistoryPage` (merges
  Phase 3 `learning_activities` and Phase 4 `test_attempts` into one
  newest-first timeline client-side — no unified backend endpoint for this).
- Every mastery/readiness figure renders "Not enough data yet." whenever the
  API's `has_data` flag is false — never a bare `0%`, which would misreport
  "measured zero" instead of "no measurement."
- Dashboard's practice grid grew to 4 tiles (Flashcards, Quiz, Tests,
  Progress) with a responsive 2-col/4-col grid.
- `src/services/progressApi.ts`, `src/types/progress.ts`; added
  `fetchActivityHistory` to `activityApi.ts`.
- Test tooling: Vitest + RTL, 27 tests total (added `ProgressPage.test.tsx`,
  `MistakesPage.test.tsx`, `ActivityHistoryPage.test.tsx`).

## Backend

- `app/repositories/skill_repository.py` — `learner_skills`, one document
  per `(user_id, category, concept)`; `record_result()` increments
  `correct_count`/`incorrect_count` via `$inc` (which creates the field from
  the increment if absent — no `$setOnInsert` conflict) and updates
  `last_seen`; `list_mistakes()` filters to `incorrect_count > 0`, sorted
  descending.
- `app/services/learner_model_service.py` — `get_progress()` aggregates
  `learner_skills` into per-category and overall pooled accuracy
  (`sum(correct) / sum(correct+incorrect)`, not an unweighted average of
  per-concept masteries), each with a `has_data` flag; estimated JLPT
  readiness requires **both** a `jlpt_target` on the profile **and**
  ≥5 combined vocabulary+grammar attempts before reporting a score.
- **Enhanced Phase 3/4 services to feed the skill model**: `ActivityService`
  now takes a `LearnerSkillRepository` and calls `record_result()` per
  answer/reviewed item in both `submit_quiz` and `complete_flashcards`
  (flashcards needed a new lookup of reviewed items' concepts — it
  previously only counted booleans); `TestService` does the same in
  `submit_attempt`, using each *question's own* category (not the test's,
  since a "mixed" test has no single category to attribute a skill update to).
- `app/api/progress.py` (`GET /api/progress`), `app/api/mistakes.py`
  (`GET /api/mistakes`), and a new `GET /api/activities/history` (exposing
  `ActivityRepository.list_by_user`, which existed since Phase 3 but was
  never routed).
- Test tooling: pytest, 59 tests total (added `test_progress.py`: no-data
  baseline, mastery after a quiz, categories-without-a-source always report
  no data, readiness gating on both jlpt_target and attempt count, mistake
  occurrence/mastery math, and a cross-feature test proving flashcards *and*
  test attempts both feed the same skill model as quizzes).

## Database

- Added `learner_skills` (compound unique index on `user_id`+`category`+
  `concept`, plus a `user_id` index). No new collections for `mistakes` or a
  unified activity log — both are computed views over existing collections
  (`learner_skills` and the union of `learning_activities`+`test_attempts`,
  respectively), not separately stored. See [DATABASE.md](DATABASE.md).
- Tests clean `learner_skills` between tests (per-test state, unlike the
  shared reference content collections).

## AI

- Not implemented. Unchanged — see [AI.md](AI.md).

## Speech

- Not implemented. Unchanged.

## Testing

- Backend: pytest, 59 tests passing (health, config, auth, profile,
  activities, test engine, learner model/progress).
- Frontend: Vitest + React Testing Library, 27 tests passing.
- E2E (Playwright or similar): not yet set up — planned for a later phase.

## CI/CD

- Unchanged from Phase 1–4. Backend tests still run against a `mongo:7`
  service container in CI.

## Known Issues

- None currently tracked.

## Technical Debt

- Carried over: `POST /api/auth/logout` protected no-op; no rate limiting on
  auth/onboarding; only N5 content exists; no level picker in the practice UI.
- Kanji/reading/listening/speaking/conversation always report
  `has_data: false` in `/api/progress` — there's genuinely no content or
  activity type feeding them yet (kanji/reading/listening arrive with
  Phase 13's JLPT expansion; speaking/conversation with Phases 8–9). This is
  the intended, honest state, not a bug to fix now.
- Self-assessed flashcard reviews (`known: true/false`) are pooled into the
  same skill signal as server-verified quiz/test answers with no confidence
  weighting — a deliberate MVP simplification (see Important Decisions),
  not something masked as fully-verified data.
- `docs/ARCHITECTURE.md`'s frontend structure list doesn't yet mention a
  `stores/` entry for anything beyond auth — profile/progress/test state all
  live in TanStack Query caches by design (see Phase 2's decision to not
  duplicate server state into Zustand); worth a doc pass in a later phase if
  this becomes confusing to new contributors.

## Important Decisions

- The git repository root is `jap-jap/` nested one level inside the
  `self-project/jap-jap/` folder on disk (pre-existing `git init` + GitHub
  remote `geoff023/jap-jap` were preserved rather than re-initialized).
- `learner_skills` is the *only* new collection this phase. "Mistakes" and
  "activity history" are explicitly **not** separate stored collections —
  a mistake is just a skill record with `incorrect_count > 0`, and a unified
  activity history is a client-side merge-and-sort of two collections that
  already exist for their own reasons (Phase 3's `learning_activities`,
  Phase 4's `test_attempts`). Avoids duplicating state that would need to
  stay in sync with the sources of truth.
- Category mastery is a **pooled** accuracy rate (total correct ÷ total
  attempts across all concepts in the category), not an average of each
  concept's individual mastery — so a concept practiced 20 times counts
  proportionally more than one practiced once, which matches what "how good
  are you at vocabulary overall" should mean.
- Estimated JLPT readiness reuses the same pooled vocabulary+grammar
  accuracy as "overall Japanese" — an intentionally simple, disclosed
  approximation (there is only N5 content to measure against regardless of
  a learner's actual `jlpt_target`), gated behind both a set goal and a
  minimum attempt count (5) so a single lucky/unlucky answer can't produce a
  swingy-looking "readiness" number. The UI always labels this "Estimated"
  and states it is not an official JLPT prediction, per the master spec.
- Flashcard skill-recording required a small Phase 3 change:
  `complete_flashcards` previously only counted `known` booleans from
  client-submitted item ids without ever fetching the underlying content;
  it now fetches reviewed items to learn their `concept` before recording a
  skill result. This was a necessary, narrowly-scoped fix to let flashcards
  feed the learner model at all — not scope creep, since "connect activity
  results to learner skills" needs every activity type to carry a concept.
- A skill update is attributed to the *question's* own category for test
  attempts (not the test's `category`, which can be `"mixed"`) — a `"mixed"`
  skill category would be meaningless to aggregate against the master
  spec's fixed category list.
- `has_data` flags exist on every progress/readiness field specifically so
  the frontend never has to infer "no data" from a suspicious-looking `0`.
  Never fabricate scores, per the master spec — an absent measurement and a
  measured zero must render differently.

## Next Phase

Phase 6 — Gemini AI Tutor (AIService → GeminiService abstraction; grammar,
vocabulary, and mistake explanations; structured Gemini responses validated
with Pydantic; Gemini mocked in all automated tests; no real API key in the
repository or CI)
