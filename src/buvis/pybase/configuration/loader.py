from __future__ import annotations

import os
import re
from pathlib import Path


DEFAULT_CONFIG_DIRECTORY = Path(
    os.getenv("BUVIS_CONFIG_DIR", Path.home() / ".config" / "buvis"),
)

_ENV_PATTERN = re.compile(r"\$\{([^}:]+)(?::-([^}]*))?\}")


class ConfigurationLoader:
    """Load YAML configs with env var substitution. Provides static methods for loading configuration files with support for environment variable interpolation using ${VAR} or ${VAR:-default} syntax."""

    @staticmethod
    def _get_search_paths() -> list[Path]:
        """Build ordered list of config directories to search.

        Returns:
            list[Path]: Search paths from highest to lowest priority:
                1. BUVIS_CONFIG_DIR (if set and non-empty)
                2. XDG_CONFIG_HOME/buvis (or ~/.config/buvis if XDG unset)
                3. ~/.buvis (legacy)
                4. Current working directory
        """
        paths: list[Path] = []

        # 1. Explicit override - highest priority
        if env_dir := os.getenv("BUVIS_CONFIG_DIR"):
            if env_dir:  # Empty string treated as unset
                paths.append(Path(env_dir).expanduser())

        # 2. XDG standard location
        xdg = os.getenv("XDG_CONFIG_HOME", "")
        xdg_path = Path(xdg).expanduser() if xdg else Path.home() / ".config"
        paths.append(xdg_path / "buvis")

        # 3. Legacy location
        paths.append(Path.home() / ".buvis")

        # 4. Project-local (lowest priority)
        paths.append(Path.cwd())

        return paths

    @staticmethod
    def _get_candidate_files(paths: list[Path], tool_name: str | None) -> list[Path]:
        """Generate candidate config file paths from search locations.

        Args:
            paths: Base directories to search for config files.
            tool_name: Optional tool name for tool-specific configs.

        Returns:
            Ordered list of candidate paths (buvis.yaml + buvis-{tool}.yaml per location).
        """
        candidates: list[Path] = []
        for base in paths:
            candidates.append(base / "buvis.yaml")
            if tool_name:
                candidates.append(base / f"buvis-{tool_name}.yaml")
        return candidates

    @staticmethod
    def find_config_files(tool_name: str | None = None) -> list[Path]:
        """Find configuration files that apply to a tool.

        Args:
            tool_name: Optional tool identifier used to narrow the search scope.

        Returns:
            list[Path]: Config file paths ordered from highest to lowest priority.

        Raises:
            NotImplementedError: Always raised until configuration discovery is implemented.
        """

        message = (
            "ConfigurationLoader.find_config_files is not implemented yet."
            f" Expected to inspect {DEFAULT_CONFIG_DIRECTORY} or tool-specific paths."
        )
        raise NotImplementedError(message)
