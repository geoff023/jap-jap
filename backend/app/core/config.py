from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolved relative to this file, not the process's current working
# directory — pydantic-settings' env_file paths are otherwise CWD-relative,
# which breaks whenever the app is launched from a directory other than
# backend/ (e.g. `uvicorn --app-dir backend app.main:app` from the repo
# root only adds backend/ to sys.path, it doesn't chdir there).
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_REPO_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables / .env.

    AI and speech credentials are optional: the app must start and the health
    endpoint must work even when they are missing.
    """

    mongodb_uri: str = "mongodb://localhost:27017/japjap"
    mongo_server_selection_timeout_ms: int = 1000

    jwt_secret: str = "dev-secret-change-me"
    jwt_expires_minutes: int = 60

    gemini_api_key: str | None = None
    stt_api_key: str | None = None

    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=(str(_REPO_ROOT / ".env"), str(_BACKEND_DIR / ".env")),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def ai_enabled(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def stt_enabled(self) -> bool:
        return bool(self.stt_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
