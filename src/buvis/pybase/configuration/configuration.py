from __future__ import annotations

import os
import platform
import warnings
from pathlib import Path

import yaml

from buvis.pybase.configuration.exceptions import ConfigurationKeyNotFoundError
from buvis.pybase.configuration.loader import ConfigurationLoader


class Configuration:
    """Manages global runtime configuration for BUVIS scripts.

    Provides functionality to load from YAML file, access, and modify
    configuration settings.

    If no configuration file path is provided, uses auto-discovery via
    ``ConfigurationLoader.find_config_files()``. Falls back to
    ``BUVIS_CONFIG_FILE`` env var (deprecated) or ``~/.config/buvis/config.yaml``.
    """

    def __init__(
        self: Configuration,
        file_path: Path | None = None,
        enable_env_substitution: bool = False,
    ) -> None:
        """Initialize Configuration with a YAML configuration file.

        Args:
            file_path: Optional path to config file. If not provided, uses
                auto-discovery or falls back to ~/.config/buvis/config.yaml.
            enable_env_substitution: If True, enables ${VAR} and ${VAR:-default}
                substitution in YAML files. Defaults to False for backward compat.

        Raises:
            FileNotFoundError: If explicit file_path doesn't exist.
        """
        self._enable_env_substitution = enable_env_substitution
        self._config_dict: dict[str, object] = {}

        existing_file_path = self._determine_config_path(file_path)

        if existing_file_path is not None:
            self.path_config_file = existing_file_path
            self._load_configuration()

        # Set hostname after load to preserve it
        self._config_dict["hostname"] = platform.node()

    def copy(self: Configuration, key: str) -> Configuration:
        """Create a copy of this configuration, optionally scoped to a key.

        Args:
            key: If provided, the copy contains only the nested dict at this key.

        Returns:
            A new Configuration instance.
        """
        copied_configuration = Configuration(self.path_config_file)

        if key:
            copied_configuration._config_dict = {}
            copied_configuration._config_dict = self.get_configuration_item(key)

        return copied_configuration

    def _determine_config_path(
        self: Configuration,
        file_path: Path | None,
    ) -> Path | None:
        """Determine the configuration file path.

        Resolution order:
            1. Explicit file_path (raises FileNotFoundError if missing)
            2. Auto-discovery via ConfigurationLoader.find_config_files()
            3. BUVIS_CONFIG_FILE env var (deprecated, emits warning)
            4. ~/.config/buvis/config.yaml default

        Args:
            file_path: Optional explicit path to config file.

        Returns:
            Absolute path to config file, or None if no config found.

        Raises:
            FileNotFoundError: If explicit file_path doesn't exist.

        .. deprecated::
            BUVIS_CONFIG_FILE env var is deprecated. Place config in standard
            locations discovered by ConfigurationLoader.
        """
        if file_path is not None:
            resolved_file_path = file_path.resolve()
            if resolved_file_path.exists():
                return resolved_file_path.absolute()
            message = f"The configuration file at {file_path} was not found."
            raise FileNotFoundError(message)

        # Try auto-discovery first
        discovered = ConfigurationLoader.find_config_files()
        if discovered:
            return discovered[0]  # Highest priority file

        # Fallback to BUVIS_CONFIG_FILE (deprecated) or default
        env_config = os.getenv("BUVIS_CONFIG_FILE")
        if env_config is not None:
            warnings.warn(
                "BUVIS_CONFIG_FILE is deprecated. Place config in standard locations.",
                DeprecationWarning,
                stacklevel=3,
            )
            alternative_file_path = Path(env_config)
        else:
            alternative_file_path = Path.home() / ".config/buvis/config.yaml"

        if alternative_file_path.exists():
            return alternative_file_path.absolute()

        return None

    def _load_configuration(self: Configuration) -> None:
        """Load configuration from the YAML file.

        Uses ConfigurationLoader when env substitution is enabled,
        otherwise uses plain yaml.safe_load for backward compatibility.
        """
        if self._enable_env_substitution:
            self._config_dict = ConfigurationLoader.load_yaml(self.path_config_file)
        else:
            with self.path_config_file.open("r") as file:
                self._config_dict = yaml.safe_load(file) or {}

    def set_configuration_item(self: Configuration, key: str, value: object) -> None:
        """Set or update a configuration item.

        Args:
            key: The configuration item key.
            value: The value to associate with the key.
        """
        self._config_dict[key] = value

    def get_configuration_item(
        self: Configuration,
        key: str,
        default: object | None = None,
    ) -> object:
        """Retrieve a configuration item by key.

        Args:
            key: The configuration item key to retrieve.
            default: Optional default value if key not found.

        Returns:
            The configuration value.

        Raises:
            ConfigurationKeyNotFoundError: If key not found and no default.
        """
        if key in self._config_dict:
            return self._config_dict[key]

        if default:
            return default

        error_message = f"{key} not found in configuration."
        raise ConfigurationKeyNotFoundError(error_message)

    def get_configuration_item_or_default(
        self: Configuration,
        key: str,
        default: object,
    ) -> object:
        """Retrieve a configuration item by key, with fallback.

        Args:
            key: The configuration item key to retrieve.
            default: Default value if key not found.

        Returns:
            The configuration value or the default.
        """
        if key in self._config_dict:
            return self._config_dict[key]

        return default

    def __repr__(self: Configuration) -> str:
        return f"---\n{yaml.dump(self._config_dict, default_flow_style=False)}"
