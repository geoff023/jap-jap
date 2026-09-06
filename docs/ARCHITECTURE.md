# Architecture

## Overview

JapJap is a monorepo with a React/TypeScript frontend and a Python/FastAPI
backend, backed by MongoDB.

```
frontend/  React + TypeScript + Vite + Tailwind CSS
backend/   FastAPI + Pydantic + MongoDB (Motor async driver)
docs/      Architecture, API, database, and AI documentation
```

## Product Model

The core learning loop the whole system is built around:

```
Learning → Practice → Assessment → Learner Model → Weakness Detection
   → Adaptive Recommendation → More Practice
```

AI (Gemini) enhances this loop — explanations, conversation, content
generation, feedback — but deterministic logic (scoring, XP, mastery,
recommendation ranking) always lives in backend services, never in the AI.

## Backend Layering

```
routes (app/api) → services (app/services) → repositories (app/repositories) → MongoDB
```

* **Routes** parse/validate the HTTP request (via Pydantic schemas) and
  delegate to a service. No business logic here.
* **Services** contain business logic and orchestrate repositories.
* **Repositories** are the only layer that talks to MongoDB.

## AI Abstraction

```
AIService
    ↓
GeminiService
```

All Gemini calls go through `AIService`, implemented by `GeminiService`, so
the app is never tightly coupled to a single AI provider. AI output is
treated as untrusted and validated with Pydantic before touching business
logic or the database:

```
Gemini → structured output → Pydantic validation → business validation → database
```

Gemini never writes to the database directly.

## Speech Abstraction

```
SpeechToTextService
    ↓
STTProvider
```

Speech-to-text follows the same pattern: application code depends on
`SpeechToTextService`, backed by a swappable `STTProvider` implementation.

## Frontend Structure

```
frontend/src/
├── components/   # reusable UI components
├── pages/        # route-level views
├── layouts/      # shared page layouts
├── hooks/        # custom React hooks
├── services/      # API client functions
├── stores/       # Zustand stores
├── types/        # shared TypeScript types
└── utils/        # helpers
```

State: TanStack Query for server state (API data), Zustand for local/UI
state where a store genuinely helps.

## Configuration & Secrets

All configuration comes from environment variables (see `.env.example`).
AI and speech credentials are optional — the backend must start and
`/api/health` must succeed even when `GEMINI_API_KEY` / `STT_API_KEY` are
unset.

## Phased Development

The project is built in explicit phases (see
[docs/PROJECT_STATE.md](PROJECT_STATE.md)). Each phase is scoped, tested,
verified, documented, and committed before the next one begins.
