"""Buvis application settings modeled via environment variables."""

from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class BuvisSettings(BaseSettings):
    """Base settings shared by Buvis services using the ``BUVIS_`` prefix."""

    model_config = SettingsConfigDict(
        env_prefix="BUVIS_",
        case_sensitive=False,
        frozen=True,
        extra="forbid",
    )

    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
