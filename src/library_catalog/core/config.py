from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Library Catalog API"
    environment: Literal[
        "development",
        "staging",
        "production",
    ] = "development"
    debug: bool = True
    database_url: PostgresDsn

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()