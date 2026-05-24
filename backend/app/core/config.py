from functools import lru_cache
from pathlib import Path

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: PostgresDsn = "postgresql+psycopg2://postgres:postgres@localhost:5432/meetingpilot"

    # Application
    APP_NAME: str = "MeetingPilot API"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Storage
    UPLOAD_DIR: str = "uploads/audio"

    # Vector
    EMBEDDING_DIMENSION: int = 1536

    @computed_field
    @property
    def DATABASE_URL_STR(self) -> str:
        return str(self.DATABASE_URL)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
