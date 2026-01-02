"""Example nested settings demonstrating env delimiter overrides."""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PoolSettings(BaseModel):
    """Connection pool sizing.

    Attributes:
        min_size: Minimum number of connections to keep in the pool.
        max_size: Maximum number of connections the pool can reach.
    """

    min_size: int = 5
    max_size: int = 20


class DatabaseSettings(BaseModel):
    """Database connection configuration."""

    url: str = ""
    pool: PoolSettings = Field(default_factory=PoolSettings)


class PayrollSettings(BaseSettings):
    """Settings that can be overridden with nested env vars.

    The ``env_nested_delimiter`` of ``"__"`` allows setting deeply nested values
    such as ``BUVIS_PAYROLL_DATABASE_POOL__MIN_SIZE`` to customize
    ``database.pool.min_size`` without touching the rest of the model.
    """

    model_config = SettingsConfigDict(
        env_prefix="BUVIS_PAYROLL_",
        env_nested_delimiter="__",
        case_sensitive=False,
        frozen=True,
        extra="forbid",
    )

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
