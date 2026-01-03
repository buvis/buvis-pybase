"""Convenience exports for example configuration models."""

from .complex_env_settings import (
    HCMSettings,
    PaymentRule,
    PayrollSettings as _PaymentRulesSettings,
)
from .music_settings import MusicSettings
from .nested_settings import (
    DatabaseSettings,
    PayrollSettings as NestedPayrollSettings,
    PoolSettings,
)
from .photo_settings import PhotoSettings

# Backwards-compatible alias that now refers to the JSON-rule example.
PayrollSettings = _PaymentRulesSettings

__all__ = [
    "DatabaseSettings",
    "HCMSettings",
    "MusicSettings",
    "NestedPayrollSettings",
    "PaymentRule",
    "PayrollSettings",
    "PhotoSettings",
    "PoolSettings",
]
