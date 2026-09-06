# JapJap Backend

FastAPI + Pydantic + MongoDB (Motor async driver) backend for JapJap.

See the [repository root README](../README.md) for full setup instructions.

## Structure

```
app/
├── api/            # FastAPI route handlers
├── core/           # config, database connection
├── models/         # domain models
├── schemas/        # Pydantic request/response schemas
├── services/       # business logic
├── repositories/   # MongoDB data access
├── ai/             # AIService -> GeminiService abstraction
├── speech/         # SpeechToTextService -> STTProvider abstraction
└── main.py         # app entrypoint
```

Routes call services, services call repositories, repositories talk to
MongoDB. Business logic never lives directly in route handlers.

## Scripts

```bash
uvicorn app.main:app --reload --port 8000   # run dev server
pytest                                       # run tests
ruff check .                                 # lint
black --check .                              # format check
black .                                      # auto-format
```
