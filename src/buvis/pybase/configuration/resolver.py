"""Resolve Buvis settings using the configuration loader and optional CLI overrides."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import ValidationError
from pydantic_settings import BaseSettings

from .exceptions import ConfigurationError
from .loader import ConfigurationLoader
from .source import ConfigSource
from .validators import is_sensitive_field


logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseSettings)


def _load_yaml_config(file_path: Path | None = None) -> dict[str, Any]:
    """Load YAML config, return empty dict if not found.

    Args:
        file_path: Path to YAML file. If None, uses BUVIS_CONFIG_FILE env var
            or defaults to ~/.config/buvis/config.yaml.

    Returns:
        Parsed YAML as dict, or empty dict if file doesn't exist.

    Raises:
        ConfigurationError: If YAML syntax is invalid.
    """
    if file_path is None:
        default = Path.home() / ".config" / "buvis" / "config.yaml"
        file_path = Path(os.getenv("BUVIS_CONFIG_FILE", str(default)))

    if not file_path.exists():
        return {}

    try:
        with file_path.open() as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        line_num = mark.line + 1 if mark else "unknown"
        raise ConfigurationError(
            f"YAML syntax error in {file_path}:{line_num}: {e}"
        ) from e
    except PermissionError:
        logger.warning("Permission denied reading %s, skipping", file_path)
        return {}


def _format_validation_errors(error: ValidationError) -> str:
    """Format Pydantic validation errors into user-friendly message.

    Masks error details for sensitive fields (password, token, etc.)
    to prevent secret leakage in error messages.

    Args:
        error: Pydantic ValidationError to format.

    Returns:
        Formatted error message with field paths and descriptions.
    """
    lines = []
    for err in error.errors():
        field_path = ".".join(str(loc) for loc in err["loc"])
        if is_sensitive_field(field_path):
            msg = "invalid value (hidden)"
        else:
            msg = err["msg"]
        lines.append(f"  {field_path}: {msg}")
    return "Configuration validation failed:\n" + "\n".join(lines)


class ConfigResolver:
    """Resolve Pydantic settings classes using configuration discovery."""

    def __init__(self, tool_name: str | None = None) -> None:
        """Create a resolver.

        Args:
            tool_name: Optional identifier for a CLI tool whose configs should be
                considered during discovery. Must be lowercase without hyphens.

        Raises:
            ValueError: If tool_name contains uppercase letters or hyphens.
        """
        if tool_name is not None:
            if not tool_name.islower() or "-" in tool_name:
                msg = "tool_name must be lowercase without hyphens"
                raise ValueError(msg)
        self.tool_name = tool_name
        self.loader = ConfigurationLoader()
        self._sources: dict[str, ConfigSource] = {}
        logger.debug("ConfigResolver initialized for tool %s", tool_name)

    def resolve(
        self,
        settings_class: type[T],
        config_dir: str | None = None,
        config_path: Path | None = None,
        cli_overrides: dict[str, Any] | None = None,
    ) -> T:
        """Instantiate a settings class with precedence: CLI > ENV > YAML > Defaults.

        Args:
            settings_class: The Pydantic settings class to instantiate.
            config_dir: Optional configuration directory that overrides the
                ``BUVIS_CONFIG_DIR`` environment variable for this resolution.
            config_path: Optional path to YAML config file.
            cli_overrides: Explicit overrides typically parsed from CLI options
                that take precedence over discovered configuration values.

        Returns:
            T: An instance of ``settings_class`` populated with resolved values.

        Raises:
            ConfigurationError: If validation fails for any configuration value.

        Note:
            Precedence order (highest to lowest):
            1. CLI overrides (explicit values passed in cli_overrides)
            2. Environment variables (Pydantic handles automatically)
            3. YAML config file values
            4. Model field defaults
        """
        original_config_dir = os.environ.get("BUVIS_CONFIG_DIR")

        try:
            if config_dir is not None:
                os.environ["BUVIS_CONFIG_DIR"] = config_dir
                logger.debug("Set BUVIS_CONFIG_DIR to %s", config_dir)

            # Load YAML config (priority 3)
            yaml_config = _load_yaml_config(config_path)
            logger.debug("Loaded YAML config: %s", yaml_config)

            try:
                # Create base settings with YAML + ENV (ENV overrides YAML via Pydantic)
                # Note: Pydantic kwargs override env, so we create without YAML first
                base_settings = settings_class()

                # Apply YAML for fields not set by env (check against defaults)
                merged: dict[str, Any] = {}
                for key, value in yaml_config.items():
                    if hasattr(base_settings, key):
                        field_value = getattr(base_settings, key)
                        default = settings_class.model_fields.get(key)
                        if default and field_value == default.default:
                            # Field has default value, apply YAML
                            merged[key] = value

                # Apply CLI overrides (priority 1, highest)
                if cli_overrides:
                    for key, value in cli_overrides.items():
                        if value is not None:
                            merged[key] = value

                # Build final settings
                if merged:
                    final_settings = settings_class.model_validate(
                        base_settings.model_dump() | merged
                    )
                else:
                    final_settings = base_settings

                # Track sources for each field
                env_prefix = settings_class.model_config.get("env_prefix", "")
                env_keys = {
                    k.removeprefix(env_prefix).lower()
                    for k in os.environ
                    if k.startswith(env_prefix)
                }

                self._sources.clear()
                for field in settings_class.model_fields:
                    if cli_overrides and cli_overrides.get(field) is not None:
                        self._sources[field] = ConfigSource.CLI
                    elif field in env_keys:
                        self._sources[field] = ConfigSource.ENV
                    elif field in yaml_config:
                        self._sources[field] = ConfigSource.YAML
                    else:
                        self._sources[field] = ConfigSource.DEFAULT

                self._log_sources()
                return final_settings
            except ValidationError as e:
                raise ConfigurationError(_format_validation_errors(e)) from e
        finally:
            if original_config_dir is None:
                os.environ.pop("BUVIS_CONFIG_DIR", None)
            else:
                os.environ["BUVIS_CONFIG_DIR"] = original_config_dir

    def _log_sources(self) -> None:
        """Log source of each config field at DEBUG level (no values)."""
        for field, source in self._sources.items():
            logger.debug("Config '%s' from %s", field, source.value)

    @property
    def sources(self) -> dict[str, ConfigSource]:
        """Get copy of source tracking dict."""
        return self._sources.copy()
