# JapJap Project State

## Current Phase

Phase 2 — Onboarding (complete)

## Completed

- Phase 0: Open-source foundation, dev environment, CI/CD, testing infrastructure, docs.
- Phase 1: Authentication — registration, login, logout, JWT, protected routes, auth state.
- Phase 2: Onboarding — learning goals, experience, preferred level, JLPT target, editable profile, unrestricted level changes.

## Frontend

- React + TypeScript + Vite (`frontend/`), Tailwind CSS v4 (via `@tailwindcss/vite`).
- React Router, TanStack Query, Zustand. Zustand holds auth state; TanStack
  Query owns server state for the learner profile (`useQuery`/cache updates
  on mutation, no separate profile store).
- Pages: `LandingPage`, `LoginPage`, `RegisterPage`, `OnboardingPage`
  (protected), `DashboardPage` (protected).
- `OnboardingPage` — goals (multi-select), experience (single-select),
  starting level, optional JLPT target; posts to `/api/onboarding` then
  navigates to `/dashboard`.
- `DashboardPage` — fetches `/api/profile`; if it 404s (no profile yet),
  redirects to `/onboarding` via `<Navigate>`; otherwise shows goals,
  experience-derived summary, estimated level ("Not enough data yet." when
  null — never fabricated), JLPT goal, and level-switch buttons that call
  `PATCH /api/profile` with no restriction on which level can be picked.
- `RegisterPage` now navigates to `/onboarding` after registration (not
  straight to `/dashboard`); `LoginPage` still goes to `/dashboard`, which
  itself redirects to onboarding if the profile doesn't exist yet.
- `src/services/profileApi.ts` (fetchProfile/submitOnboarding/updateProfile),
  `src/services/httpErrors.ts` (shared `ApiError`/`parseErrorMessage`,
  extracted from `authApi.ts` so `profileApi.ts` doesn't import auth code).
- `src/types/profile.ts` — types plus the option lists
  (`LEARNING_GOALS`, `EXPERIENCE_LEVELS`, `PRACTICE_LEVELS`, `JLPT_LEVELS`)
  used by both the onboarding form and the dashboard.
- Test tooling: Vitest + React Testing Library, 14 tests total (added
  `OnboardingPage.test.tsx`, `DashboardPage.test.tsx`).
- No vocabulary/grammar/flashcards, JLPT test engine, AI, or STT yet — by design.

## Backend

- FastAPI app (`backend/app/main.py`), CORS configured from `CORS_ORIGINS`.
- `app/schemas/profile.py` — `LearningGoal`, `ExperienceLevel`,
  `PracticeLevel` (N5–N1 + `conversation`), `JLPTLevel` enums;
  `OnboardingRequest` (all fields required, `goals` non-empty),
  `ProfileUpdateRequest` (all fields optional — partial update via
  `model_dump(exclude_unset=True, mode="json")`, so an explicit `null` still
  clears a field like `jlpt_target` while an omitted field is untouched).
- `app/repositories/profile_repository.py` — `learner_profiles` collection,
  keyed by `user_id` (unique index), single upsert method used by both
  onboarding (full write) and profile updates (partial merge).
- `app/services/profile_service.py` — `complete_onboarding` (sets
  `estimated_level: null` — no assessment data exists yet, never fabricated)
  and `update_profile` (raises `ProfileNotFoundError` if onboarding hasn't
  happened, translated to `404` by the route).
- `app/api/onboarding.py` — `POST /api/onboarding`.
- `app/api/profile.py` — `GET /api/profile`, `PATCH /api/profile`.
- `app/api/deps.py` — added `get_profile_repository`.
- Test tooling: pytest + pytest-asyncio + httpx, 26 tests total (added
  `test_profile.py`: onboarding validation, get/patch auth + 404 cases,
  partial-update semantics, explicit `jlpt_target` clearing, and an explicit
  N4→N3→N5→N4→conversation sequence proving no lock/order is enforced).

## Database

- MongoDB via Motor async driver.
- `users` (Phase 1) and `learner_profiles` (Phase 2, unique index on
  `user_id`) collections implemented — see [DATABASE.md](DATABASE.md).
- Local dev / CI setup unchanged from Phase 1 (real MongoDB, `japjap_test`
  database for tests, service container in CI).

## AI

- Not implemented. Unchanged — see [AI.md](AI.md).

## Speech

- Not implemented. Unchanged.

## Testing

- Backend: pytest, 26 tests passing (health, config, auth, profile/onboarding).
- Frontend: Vitest + React Testing Library, 14 tests passing (landing page,
  auth store, protected route, login, onboarding, dashboard).
- E2E (Playwright or similar): not yet set up — planned for a later phase.

## CI/CD

- Unchanged from Phase 1: frontend/backend/security workflows, backend tests
  run against a `mongo:7` service container, no real AI/STT keys anywhere.

## Known Issues

- None currently tracked.

## Technical Debt

- `POST /api/auth/logout` is still a protected no-op (carried over from
  Phase 1 — stateless JWTs, no blacklist).
- No rate limiting on `/api/auth/*` or `/api/onboarding` yet — acceptable
  pre-deployment, should be addressed before any public launch.
- No placement test — onboarding always asks the learner to pick a starting
  level directly (the master spec calls this optional for MVP).

## Important Decisions

- The git repository root is `jap-jap/` nested one level inside the
  `self-project/jap-jap/` folder on disk (pre-existing `git init` + GitHub
  remote `geoff023/jap-jap` were preserved rather than re-initialized).
- `learner_profiles` is keyed by `user_id` (a string, not `_id`) so the
  repository can use one atomic upsert for both "create on first onboarding"
  and "merge on later edits" — avoids a separate create-vs-update branch.
- Field names are snake_case throughout (`preferred_level`, not
  `preferredLevel`) for consistency with the existing `users` collection and
  with idiomatic FastAPI/Pydantic — a deliberate deviation from the
  camelCase shown in the master spec's prose examples.
- `PATCH /api/profile` requires an existing profile (404 otherwise) rather
  than silently creating one; `POST /api/onboarding` is the only way to
  create a profile, and it's idempotent (safe to resubmit).
- `preferred_level` includes a `conversation` option alongside `N5`–`N1`
  (per the master spec's example: "N5 → N4 → N3 → N5 → N4 → Conversation") —
  it is a practice-mode selector, not strictly a JLPT level, which is why it
  is a separate enum (`PracticeLevel`) from `JLPTLevel` (used only by
  `jlpt_target`, which has no `conversation` option).
- `estimated_level` is hardcoded to `null` at onboarding time and has no
  write path yet anywhere in the API — only a future learner-model phase
  should ever set it, so there's currently no way to fabricate it even by
  mistake.
- Frontend profile state is **not** kept in the Zustand auth store — it's
  TanStack Query server-cache state (`['profile']` query key), updated
  optimistically via `queryClient.setQueryData` after a successful mutation
  rather than storing a duplicate copy in a separate store.

## Next Phase

Phase 3 — Core Learning (vocabulary, grammar, flashcards, multiple choice,
sentence completion, activity completion, XP)
