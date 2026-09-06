# JapJap Project State

## Current Phase

Phase 1 — Authentication (complete)

## Completed

- Phase 0: Open-source foundation, dev environment, CI/CD, testing infrastructure, docs.
- Phase 1: Authentication — registration, login, logout, JWT, protected routes, auth state.

## Frontend

- React + TypeScript + Vite (`frontend/`), Tailwind CSS v4 (via `@tailwindcss/vite`).
- React Router, TanStack Query, Zustand installed. Zustand now used for auth
  state (`src/stores/authStore.ts`, persisted to `localStorage`).
- Pages: `LandingPage` (health badge + sign up/log in or dashboard link),
  `LoginPage`, `RegisterPage`, `DashboardPage` (protected).
- `src/components/ProtectedRoute.tsx` — redirects to `/login` when
  `isAuthenticated` is false; used to guard `/dashboard`.
- `src/services/api.ts` (health check), `src/services/authApi.ts`
  (register/login/logout/fetchMe against the backend).
- Test tooling: Vitest + React Testing Library, 9 tests across
  `App.test.tsx`, `authStore.test.ts`, `ProtectedRoute.test.tsx`,
  `LoginPage.test.tsx`.
- No onboarding, learning features, JLPT system, AI, or STT yet — by design.

## Backend

- FastAPI app (`backend/app/main.py`), CORS configured from `CORS_ORIGINS`.
- Layered structure: `api/`, `core/`, `models/`, `schemas/`, `services/`,
  `repositories/`, `ai/`, `speech/`.
- `app/core/security.py` — bcrypt password hashing, PyJWT access tokens
  (`JWT_SECRET` / `JWT_EXPIRES_MINUTES`).
- `app/repositories/user_repository.py` — `users` collection access,
  including a unique index on `email` (created on app startup, best-effort).
- `app/services/auth_service.py` — register/authenticate business logic,
  raises typed exceptions (`EmailAlreadyRegisteredError`,
  `InvalidCredentialsError`) that routes translate to HTTP errors.
- `app/api/auth.py` — `POST /api/auth/register`, `/login`, `/logout`.
- `app/api/users.py` — `GET /api/users/me` (protected).
- `app/api/deps.py` — shared `get_user_repository` / `get_current_user`
  (Bearer JWT) dependencies.
- `GET /api/health` — unchanged, still never crashes without MongoDB.
- Test tooling: pytest + pytest-asyncio + httpx, 14 tests
  (`test_health.py`, `test_config.py`, `test_auth.py`) against a real
  MongoDB test database (`japjap_test`), not a mock.

## Database

- MongoDB via Motor async driver.
- `users` collection implemented (see [DATABASE.md](DATABASE.md)): `email`
  (unique), `hashed_password`, `created_at`.
- Local dev: `docker compose up -d mongo` (mongo:7, port 27017), or any local
  MongoDB via `MONGODB_URI`. Tests use a separate `japjap_test` database on
  the same instance so they don't touch dev data.
- CI: backend tests run against a `mongo:7` GitHub Actions service container.

## AI

- Not implemented. Unchanged from Phase 0 — see [AI.md](AI.md).

## Speech

- Not implemented. Unchanged from Phase 0.

## Testing

- Backend: pytest, 14 tests passing (health, config, full auth flow:
  register, duplicate email, weak password, login success/failure,
  protected endpoint with/without/invalid token, logout).
- Frontend: Vitest + React Testing Library, 9 tests passing (landing page,
  auth store, protected route redirect/pass-through, login success/failure).
- E2E (Playwright or similar): not yet set up — planned for a later phase.

## CI/CD

- `.github/workflows/frontend.yml` — unchanged: install, lint, typecheck,
  test, build.
- `.github/workflows/backend.yml` — now runs a `mongo:7` service container
  (with a health check) so auth/repository tests exercise a real database;
  `MONGODB_URI` points at a dedicated `japjap_test` database.
- `.github/workflows/security.yml` — unchanged.
- Still no real Gemini/STT API keys required anywhere in CI. `JWT_SECRET`
  uses its non-secret dev default in CI (fine — it's not protecting anything
  real there).

## Known Issues

- None currently tracked.

## Technical Debt

- `POST /api/auth/logout` is a protected no-op (stateless JWTs, no
  blacklist). Acceptable for now; revisit if token revocation before
  natural expiry becomes a requirement.
- No rate limiting on `/api/auth/*` yet — acceptable for local/early dev,
  should be addressed before any public deployment.

## Important Decisions

- The git repository root is `jap-jap/` nested one level inside the
  `self-project/jap-jap/` folder on disk (pre-existing `git init` + GitHub
  remote `geoff023/jap-jap` were preserved rather than re-initialized).
- Auth tests run against a real MongoDB (a dedicated `japjap_test` database,
  cleaned between tests via an autouse fixture) rather than a mock database,
  both locally and in CI (via a service container) — avoids mock/real
  divergence bugs in the data layer.
- Access tokens are stateless bearer JWTs (no refresh tokens, no
  server-side session/blacklist) for MVP simplicity; `/api/auth/logout`
  exists as a protected endpoint for a clean future extension point rather
  than being purely client-side.
- Frontend logout does **not** call `navigate()` after `clearAuth()` (or
  before it) — `ProtectedRoute`'s declarative redirect-to-`/login` on
  `isAuthenticated === false` already handles it, and an extra imperative
  navigate briefly raced it (auth state updates before the router
  reconciles a new location), which was observed as a "flash to /login"
  in manual browser testing.
- `preferredLevel` / `estimatedLevel` / `jlptTarget` (Phase 2) are still not
  implemented — only noted here as a standing design decision from the
  master spec, see [DATABASE.md](DATABASE.md).

## Next Phase

Phase 2 — Onboarding (learning goals, Japanese experience, preferred level,
JLPT target, editable profile, unrestricted level changes)
