from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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
        env_file=("../.env", ".env"),
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
