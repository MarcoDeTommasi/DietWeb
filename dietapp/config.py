from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _normalise_database_url(value: str) -> str:
    """Convert provider-specific PostgreSQL URLs to a SQLAlchemy URL."""
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg2://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg2://", 1)
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    openrouter_api_key: str | None
    openrouter_api_url: str
    openrouter_model: str
    environment: str

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    local_database = f"sqlite:///{(BASE_DIR / 'dieta.db').as_posix()}"
    database_url = (
        os.getenv("DATABASE_URL_INTERNAL")
        or os.getenv("DATABASE_URL")
        or local_database
    )
    return Settings(
        database_url=_normalise_database_url(database_url),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        openrouter_api_url=os.getenv(
            "OPENROUTER_API_URL", "https://openrouter.ai/api/v1"
        ),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        environment=os.getenv("APP_ENV", "development"),
    )
