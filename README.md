# JapJap 🎌

JapJap is an open-source, AI-assisted Japanese learning platform for casual
learners, JLPT (N5–N1) candidates, and anyone who wants practical daily
Japanese conversation practice.

JapJap is not just "ChatGPT for learning Japanese." It's a structured
learning system — vocabulary, grammar, kanji, reading, listening, speaking,
and conversation — enhanced by AI, not replaced by it:

```
Learning → Practice → Assessment → Learner Model → Weakness Detection
   → Adaptive Recommendation → More Practice
```

> **Status:** Early development. See [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md)
> for the current phase and what's implemented so far.

## Three Learning Modes

* 🎮 **Explore** — vocabulary, mini stories, culture, reading, games
* 🗣️ **Speak** — AI conversation, roleplay, speech-to-text, shadowing
* 📚 **JLPT** — structured N5–N1 exam prep (vocabulary, kanji, grammar,
  reading, listening, mock exams)

All three modes feed the same persistent learner model.

## Tech Stack

| Layer    | Technology |
|----------|------------|
| Frontend | React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Zustand |
| Backend  | Python, FastAPI, Pydantic, MongoDB (async driver) |
| AI       | Google Gemini, behind an `AIService` abstraction |
| Speech   | Pluggable `SpeechToTextService` / `STTProvider` abstraction |

## Project Structure

```
japjap/
├── frontend/     # React + TypeScript + Vite app
├── backend/      # FastAPI service
├── docs/         # Architecture, API, database, and AI documentation
└── .github/      # CI/CD workflows
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Getting Started

### Prerequisites

* Node.js 20+
* Python 3.11+ (3.10 also works)
* MongoDB (local install, or via Docker)

### 1. Clone the repository

```bash
git clone https://github.com/geoff023/jap-jap.git
cd jap-jap
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Fill in local values as needed. **No real API keys are required** to run the
core app — AI-powered features simply stay disabled without a Gemini key.
If you want to try AI features, get your own free key from
[Google AI Studio](https://ai.google.dev/) and put it in your local `.env`.
Never share or commit this file.

### 3. Start MongoDB

Using Docker Compose (recommended):

```bash
docker compose up -d mongo
```

Or point `MONGODB_URI` in `.env` at any MongoDB instance you already have
running locally.

### 4. Start the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS/Linux
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Backend runs at http://localhost:8000. Health check: http://localhost:8000/api/health

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173.

### 6. Run tests

```bash
cd backend && pytest
cd frontend && npm test
```

### 7. Run linting & type checks

```bash
cd backend && ruff check . && black --check .
cd frontend && npm run lint && npm run typecheck
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

See [SECURITY.md](SECURITY.md) for how to report vulnerabilities, and for
this project's policy on secrets and API keys (never commit real ones).

## Content & Licensing

* **This project's original code** is licensed under the [MIT License](LICENSE).
* **Open-source dependencies** are used under their own respective licenses
  (see `package.json` / `requirements.txt`).
* **Third-party APIs** (e.g. Google Gemini) are used via your own API key,
  under that provider's terms — JapJap does not redistribute or bundle
  access to them.
* **JLPT-related learning material** included in this project is either
  originally written for JapJap or clearly marked as AI-generated
  supplementary content. JapJap does not redistribute official/copyrighted
  JLPT exam questions.

## License

MIT — see [LICENSE](LICENSE).
