"""Runtime settings, never sourced from user or LLM prompts."""

from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PA_", env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./assistant.db"
    mode: Literal["demo", "openai_compatible"] = "demo"
    timezone: str = "UTC"
    history_limit: int = Field(default=12, ge=1, le=30)
    history_retention_days: int = Field(default=30, ge=1, le=365)
    max_tool_calls: int = Field(default=4, ge=1, le=8)
    approval_ttl_seconds: int = Field(default=600, ge=60, le=3600)
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str | None = None
    llm_max_tokens: int = Field(default=512, ge=64, le=2048)
    llm_timeout_seconds: float = Field(default=20, ge=1, le=60)

    @field_validator("timezone")
    @classmethod
    def check_zone(cls, zone: str) -> str:
        try:
            ZoneInfo(zone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("Unknown IANA timezone") from exc
        return zone

    @field_validator("llm_base_url")
    @classmethod
    def check_base_url(cls, url: str) -> str:
        if not url.startswith("https://") or "@" in url:
            raise ValueError("LLM base URL must be HTTPS and contain no credentials")
        return url.rstrip("/")


settings = Settings()
