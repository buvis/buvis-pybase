"""Buvis application settings modeled via environment variables."""

from __future__ import annotations

import re
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


_VALID_ENV_PATTERN = re.compile(r"^BUVIS_[A-Z][A-Z0-9_]*$")


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


def validate_env_var_name(name: str) -> bool:
    """Check if env var name follows BUVIS convention.

    Rules:
    - Must start with BUVIS_
    - SCREAMING_SNAKE_CASE only
    - No hyphens (env vars don't support them anyway)
    - At least one char after prefix

    Args:
        name: Environment variable name to validate.

    Returns:
        True if valid, False otherwise.
    """
    return bool(_VALID_ENV_PATTERN.match(name))


def assert_valid_env_var_name(name: str) -> None:
    """Validate env var name and raise if invalid.

    Args:
        name: Environment variable name to validate.

    Raises:
        ValueError: If name doesn't follow BUVIS naming convention.
    """
    if not validate_env_var_name(name):
        raise ValueError(
            f"Invalid env var name '{name}'. "
            "Must match BUVIS_{{TOOL}}_{{FIELD}} in SCREAMING_SNAKE_CASE"
        )


def validate_tool_name(tool_name: str) -> None:
    """Validate tool name is SCREAMING_SNAKE_CASE.

    Args:
        tool_name: Tool identifier to validate.

    Raises:
        ValueError: If tool_name contains hyphens or is not uppercase.
    """
    if not tool_name.isupper() or "-" in tool_name:
        raise ValueError(f"Tool name must be SCREAMING_SNAKE_CASE, got: {tool_name}")


def create_tool_settings_class(
    tool_name: str,
    **field_definitions: tuple[type, object],
) -> type[BaseSettings]:
    """Factory for tool-specific settings classes.

    Creates a BaseSettings subclass with:
    - env_prefix = BUVIS_{TOOL}_
    - case_sensitive = False
    - frozen = True
    - extra = "forbid"

    Args:
        tool_name: Tool identifier in SCREAMING_SNAKE_CASE.
        **field_definitions: Field name to (type, default) tuples.

    Returns:
        A new BaseSettings subclass.

    Raises:
        ValueError: If tool_name is not SCREAMING_SNAKE_CASE.

    Example:
        PayrollSettings = create_tool_settings_class(
            "PAYROLL",
            batch_size=(int, 1000),
        )
    """
    validate_tool_name(tool_name)

    config = SettingsConfigDict(
        env_prefix=f"BUVIS_{tool_name}_",
        case_sensitive=False,
        frozen=True,
        extra="forbid",
    )

    # Build class name: PAYROLL -> PayrollSettings, USER_AUTH -> UserauthSettings
    class_name = f"{tool_name.title().replace('_', '')}Settings"

    # Convert field_definitions to class attributes
    namespace: dict[str, object] = {"model_config": config}
    annotations: dict[str, type] = {}

    for name, (field_type, default) in field_definitions.items():
        namespace[name] = default
        annotations[name] = field_type

    namespace["__annotations__"] = annotations

    return type(class_name, (BaseSettings,), namespace)
