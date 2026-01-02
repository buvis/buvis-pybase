"""Convenience exports for example configuration models."""

from .complex_env_settings import PaymentRule, PayrollSettings as _PaymentRulesSettings
from .nested_settings import (
    DatabaseSettings,
    PayrollSettings as NestedPayrollSettings,
    PoolSettings,
)

# Backwards-compatible alias that now refers to the JSON-rule example.
PayrollSettings = _PaymentRulesSettings

__all__ = [
    "PoolSettings",
    "DatabaseSettings",
    "NestedPayrollSettings",
    "PaymentRule",
    "PayrollSettings",
]
