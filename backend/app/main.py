from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.users import router as users_router
from app.core.config import get_settings
from app.core.database import close_client, get_database
from app.repositories.user_repository import UserRepository

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await UserRepository(get_database()).ensure_indexes()
    except Exception:
        # MongoDB may be unavailable (e.g. local dev without it running yet);
        # the app should still start, and /api/health reports the DB status.
        pass
    yield
    close_client()


app = FastAPI(title="JapJap API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/users", tags=["users"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "JapJap API"}
