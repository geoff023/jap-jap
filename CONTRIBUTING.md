# Contributing to JapJap

Thanks for your interest in contributing! JapJap is built incrementally,
phase by phase — please read this guide before opening a PR.

## Ground Rules

* **No secrets, ever.** Never commit API keys, credentials, tokens, or
  personal data. See [SECURITY.md](SECURITY.md).
* **No copyrighted JLPT content.** Do not add official JLPT past papers or
  other copyrighted exam material you don't have the right to redistribute.
  Use original, clearly-licensed, or clearly-marked AI-generated content.
* **Keep changes scoped.** Prefer small, focused PRs over large ones that mix
  unrelated concerns.

## Project Structure

```
japjap/
├── frontend/   # React + TypeScript + Vite + Tailwind
├── backend/    # FastAPI + Pydantic + MongoDB
├── docs/       # Architecture, API, database, and AI documentation
└── .github/    # CI/CD workflows
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full architecture.

## Local Development Setup

1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in local values (no real API keys
   are required to run the app — AI features degrade gracefully without one).
3. Start MongoDB (locally, or via `docker compose up -d mongo`).
4. Install and run the backend:
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt -r requirements-dev.txt
   uvicorn app.main:app --reload --port 8000
   ```
5. Install and run the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
6. Run tests:
   ```bash
   cd backend && pytest
   cd frontend && npm test
   ```
7. Run linting:
   ```bash
   cd backend && ruff check . && black --check .
   cd frontend && npm run lint && npm run typecheck
   ```

## Branching

* `main` is the stable branch.
* Create feature branches off `main`, named like:
  `feature/authentication`, `feature/jlpt-tests`, `fix/login-error`.

## Commit Messages

Use clear, descriptive, conventional-style commit messages:

```
feat: add authentication
fix: handle expired JWT
chore: add CI pipeline
docs: update API reference
```

Avoid meaningless commits like `update`, `changes`, `final`.

## Pull Requests

* Ensure tests, linting, and type checks pass locally before opening a PR.
* CI must pass without requiring any real API keys — AI-related tests must
  mock the Gemini/STT services.
* Describe what changed and why.

## Code Organization Rules

* Business logic belongs in `services/`, not in route handlers
  (`routes → services → repositories → MongoDB`).
* All Gemini calls go through the `AIService` → `GeminiService` abstraction.
* All speech-to-text calls go through the `SpeechToTextService` → `STTProvider`
  abstraction.
* Gemini output is untrusted: validate with Pydantic before it touches the
  database. AI must never write to the database directly.

## Questions

Open a GitHub issue for discussion before starting significant work.
