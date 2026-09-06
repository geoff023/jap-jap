# AI

**Status: not yet implemented.** This document describes the intended design
so future phases build toward a consistent architecture. No AI code exists
in Phase 0 — only the `GEMINI_API_KEY` / `STT_API_KEY` configuration
placeholders in `.env.example` and `app/core/config.py`.

## Provider

JapJap uses the [Google Gemini API](https://ai.google.dev/) for AI features.
Each contributor supplies their own API key locally — no key is ever
committed to the repository, checked into CI, or shared by the project.

## Abstraction

```
AIService
    ↓
GeminiService
```

Application code depends on an `AIService` interface, not on the Gemini SDK
directly. `GeminiService` is the concrete implementation. This keeps Gemini
calls out of routes/services scattered across the codebase and makes the
provider swappable.

## Data Flow

```
Gemini → structured output → Pydantic validation → business validation → database
```

AI responses are **untrusted generated data**:

* Gemini must return structured (e.g. JSON) output.
* Output is validated against a Pydantic schema before use.
* Business rules are validated separately (e.g. an AI-generated question
  must reference a real concept/level).
* Gemini never writes to the database directly — only application code does,
  after validation.

## What Gemini Is (and Isn't) Used For

**Used for:** grammar/vocabulary/mistake explanations, conversation,
content generation (exercises, mini stories, comprehension questions),
personalized natural-language feedback, semantic analysis.

**Not used for:** XP, scoring, progress arithmetic, authentication,
database operations, or deterministic ranking — those stay in backend
business logic so they're consistent, testable, and free of AI cost/latency.

## Graceful Degradation

The application must run, and `/api/health` must succeed, with no
`GEMINI_API_KEY` set. AI-dependent features should detect a missing key
(`Settings.ai_enabled`) and respond accordingly rather than crashing.

## Testing

Automated tests never call the real Gemini API. AI-dependent behavior is
tested against a mocked `AIService`, so CI never needs a real API key.

## Privacy

* Only the minimum context needed for a given AI feature is sent to Gemini.
* Learner data is not used to train any model.
* AI interactions may be logged for debugging/product purposes (see
  `ai_interactions` in [DATABASE.md](DATABASE.md)) but are not shared with
  other users and are excluded from public logs.

## Speech-to-Text

Mirrors the AI abstraction:

```
SpeechToTextService
    ↓
STTProvider
```

Also unimplemented in Phase 0; see Phase 9 in
[PROJECT_STATE.md](PROJECT_STATE.md).
