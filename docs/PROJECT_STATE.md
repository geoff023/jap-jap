# JapJap Project State

## Current Phase

Phase 0 — Open-Source Foundation (complete)

## Completed

- Phase 0: Open-source foundation, dev environment, CI/CD, testing infrastructure, docs.

## Frontend

- React + TypeScript + Vite (`frontend/`), Tailwind CSS v4 (via `@tailwindcss/vite`).
- React Router, TanStack Query, Zustand installed (Zustand not yet used — no
  global client state needed until later phases).
- Landing page (`src/pages/LandingPage.tsx`) shows the three learning modes
  (Explore / Speak / JLPT) and a live backend health badge.
- `src/services/api.ts` — minimal fetch client, `fetchHealth()`.
- Test tooling: Vitest + React Testing Library (`src/App.test.tsx`, 2 tests).
- Scripts: `dev`, `build`, `lint` (oxlint), `typecheck` (`tsc -b --noEmit`), `test`.
- No authentication, learning features, JLPT system, AI, or STT yet — by design.

## Backend

- FastAPI app (`backend/app/main.py`), CORS configured from `CORS_ORIGINS`.
- Layered structure created per architecture doc: `api/`, `core/`, `models/`,
  `schemas/`, `services/`, `repositories/`, `ai/`, `speech/` (all empty except
  `core` and `api/health.py` — populated as later phases need them).
- `app/core/config.py` — Pydantic Settings, reads `.env` (repo root or
  `backend/.env`), all AI/speech fields optional.
- `app/core/database.py` — lazy async MongoDB client (Motor), never raises on
  construction; connection failures are caught, not propagated.
- `GET /api/health` — returns `{"status": "ok", "database": "connected" |
  "unavailable"}`; never crashes even without MongoDB running.
- Test tooling: pytest + pytest-asyncio + httpx (`backend/tests/`, 3 tests).
- Scripts: `pytest`, `ruff check .`, `black --check .`.

## Database

- MongoDB via Motor async driver. No collections implemented yet.
- Local dev: `docker compose up -d mongo` (mongo:7, port 27017) or any local
  MongoDB instance via `MONGODB_URI`.
- Verified locally: `/api/health` returns `"database": "connected"` against a
  running local MongoDB instance.
- See [DATABASE.md](DATABASE.md) for planned collections/indexes.

## AI

- Not implemented. `GEMINI_API_KEY` is an optional config field only
  (`Settings.gemini_api_key`, `Settings.ai_enabled`). No `AIService` /
  `GeminiService` code yet — see [AI.md](AI.md) for the planned design.
- Verified: app starts and `/api/health` succeeds with no `GEMINI_API_KEY` set.

## Speech

- Not implemented. `STT_API_KEY` is an optional config field only
  (`Settings.stt_api_key`, `Settings.stt_enabled`). No `SpeechToTextService` /
  `STTProvider` code yet.

## Testing

- Backend: pytest, 3 tests passing (`test_health.py`, `test_config.py`).
- Frontend: Vitest + React Testing Library, 2 tests passing (`App.test.tsx`).
- E2E (Playwright or similar): not yet set up — planned for a later phase.

## CI/CD

- `.github/workflows/frontend.yml` — install, lint, typecheck, test, build.
- `.github/workflows/backend.yml` — install, lint (ruff), format check
  (black), test (pytest).
- `.github/workflows/security.yml` — gitleaks secret scan, `npm audit`,
  `pip-audit`.
- All CI jobs run without any real API keys or a live MongoDB instance.

## Known Issues

- None currently tracked.

## Technical Debt

- None yet — codebase is intentionally minimal at this stage.

## Important Decisions

- The git repository root is `jap-jap/` nested one level inside the
  `self-project/jap-jap/` folder on disk (pre-existing `git init` + GitHub
  remote `geoff023/jap-jap` were preserved rather than re-initialized).
- Tailwind CSS v4 was installed (latest at scaffold time) using the
  `@tailwindcss/vite` plugin rather than a `tailwind.config.js` + PostCSS
  setup (v4's recommended approach for Vite projects).
- `create-vite`'s current React+TS template ships `oxlint` instead of ESLint;
  kept as-is rather than swapping tooling with no functional need to.
- A single root-level `.env.example` / `.env` is shared by both frontend
  (`VITE_*` vars) and backend, per the master spec's example — not one file
  per app.
- `docs/AI.md` and the `ai`/`speech` backend packages exist as documentation
  and structure only; no AI or STT code has been written yet (explicitly out
  of scope for Phase 0).

## Next Phase

Phase 1 — Authentication (registration, login, logout, JWT, protected routes)
