from __future__ import annotations

import os
from pathlib import Path


DEFAULT_CONFIG_DIRECTORY = Path(
    os.getenv("BUVIS_CONFIG_DIR", Path.home() / ".config" / "buvis"),
)


class ConfigurationLoader:
    """Locate configuration files for BUVIS tools."""

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
