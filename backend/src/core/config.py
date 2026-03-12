"""
환경 변수 관리 — Pydantic BaseSettings, @lru_cache 싱글톤.
"""
from functools import lru_cache
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "eng_edu"
    debug: bool = False
    secret_key: str = "change-me-in-production-min-32-chars!!"

    # DB (postgresql+asyncpg://...)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/eng_edu"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    @field_validator("secret_key")
    @classmethod
    def secret_key_min_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
