"""Example settings demonstrating JSON array env parsing."""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PaymentRule(BaseModel):
    """Single payment rule definition.

    Attributes:
        rule_id: Unique identifier for the rule.
        enabled: Whether the rule should be active.
        bonus_pct: Optional percentage bonus that applies when the rule matches.
    """

    rule_id: str
    enabled: bool
    bonus_pct: float | None = None


class PayrollSettings(BaseSettings):
    """Settings allowing JSON string env overrides for payment rules.

    Example:
        The ``payment_rules`` field can be overridden by setting the
        ``BUVIS_PAYROLL_PAYMENT_RULES`` environment variable to a JSON list::

            [
                {"rule_id": "holiday", "enabled": true, "bonus_pct": 0.05},
                {"rule_id": "fee-waiver", "enabled": false}
            ]
    """

    model_config = SettingsConfigDict(
        env_prefix="BUVIS_PAYROLL_",
        case_sensitive=False,
        frozen=True,
        extra="forbid",
    )

    payment_rules: list[PaymentRule] = Field(default_factory=list)
    batch_size: int = 1000


class HCMSettings(BaseSettings):
    """HCM settings demonstrating dict parsing from JSON.

    Env vars:
        BUVIS_HCM_HEADERS: JSON object for HTTP headers.
        BUVIS_HCM_API_URL: API endpoint URL.

    Example:
        export BUVIS_HCM_HEADERS='{"Authorization":"Bearer xxx","X-Api-Key":"yyy"}'
    """

    model_config = SettingsConfigDict(
        env_prefix="BUVIS_HCM_",
        case_sensitive=False,
        frozen=True,
        extra="forbid",
    )

    headers: dict[str, str] = Field(default_factory=dict)
    api_url: str = ""
