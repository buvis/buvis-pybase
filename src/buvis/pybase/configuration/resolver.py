"""Resolve Buvis settings using the configuration loader and optional CLI overrides."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic_settings import BaseSettings

from .loader import ConfigurationLoader


logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseSettings)


def _load_yaml_config(file_path: Path | None = None) -> dict[str, Any]:
    """Load YAML config, return empty dict if not found.

    Args:
        file_path: Path to YAML file. If None, uses BUVIS_CONFIG_FILE env var
            or defaults to ~/.config/buvis/config.yaml.

    Returns:
        Parsed YAML as dict, or empty dict if file doesn't exist.
    """
    if file_path is None:
        default = Path.home() / ".config" / "buvis" / "config.yaml"
        file_path = Path(os.getenv("BUVIS_CONFIG_FILE", str(default)))

    if not file_path.exists():
        return {}

    with file_path.open() as f:
        return yaml.safe_load(f) or {}


class ConfigResolver:
    """Resolve Pydantic settings classes using configuration discovery."""

    def __init__(self, tool_name: str | None = None) -> None:
        """Create a resolver.

        Args:
            tool_name: Optional identifier for a CLI tool whose configs should be
                considered during discovery.
        """

        self.tool_name = tool_name
        self.loader = ConfigurationLoader()
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

        Note:
            Precedence order (highest to lowest):
            1. CLI overrides (explicit values passed in cli_overrides)
            2. Environment variables (Pydantic handles automatically)
            3. YAML config file values
            4. Model field defaults
        """
        if config_dir is not None:
            os.environ["BUVIS_CONFIG_DIR"] = config_dir
            logger.debug("Set BUVIS_CONFIG_DIR to %s", config_dir)

        # Load YAML config (priority 3)
        yaml_config = _load_yaml_config(config_path)
        logger.debug("Loaded YAML config: %s", yaml_config)

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

        # Return settings with merged overrides
        if merged:
            return base_settings.model_copy(update=merged)
        return base_settings
