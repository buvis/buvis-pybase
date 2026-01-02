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
        cli_overrides: dict[str, Any] | None = None,
    ) -> T:
        """Instantiate a settings class after discovering configuration files.

        Args:
            settings_class: The Pydantic settings class to instantiate.
            config_dir: Optional configuration directory that overrides the
                ``BUVIS_CONFIG_DIR`` environment variable for this resolution.
            cli_overrides: Explicit overrides typically parsed from CLI options
                that take precedence over discovered configuration values.

        Returns:
            T: An instance of ``settings_class`` populated with resolved values.
        """

        if config_dir is not None:
            os.environ["BUVIS_CONFIG_DIR"] = config_dir
            logger.debug("Set BUVIS_CONFIG_DIR to %s", config_dir)

        config_files = self.loader.find_config_files(tool_name=self.tool_name)
        logger.debug("Discovered config files: %s", config_files)

        overrides = cli_overrides or {}
        return settings_class(**overrides)
