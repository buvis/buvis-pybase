"""Generate YAML config templates from pydantic settings classes."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic_settings import BaseSettings


class ConfigWriter:
    """Generate YAML config templates from pydantic settings classes.

    Provides static methods to introspect pydantic-settings models and
    generate documented YAML configuration templates. Follows the static
    utility class pattern used by DirTree and StringOperator.

    Example:
        >>> from buvis.pybase.configuration import ConfigWriter
        >>> ConfigWriter.write(MySettings, Path('config.yaml'), 'mytool')
    """

    @staticmethod
    def write(
        settings_class: type[BaseSettings], output_path: Path, command_name: str
    ) -> None:
        """Write YAML config template to file.

        Args:
            settings_class: The pydantic-settings class to introspect.
            output_path: Destination path for the YAML file.
            command_name: Name used in YAML header comment.

        Raises:
            NotImplementedError: Method not yet implemented.
        """
        raise NotImplementedError

    @staticmethod
    def generate(settings_class: type[BaseSettings], command_name: str) -> str:
        """Generate YAML config string.

        Args:
            settings_class: The pydantic-settings class to introspect.
            command_name: Name used in YAML header comment.

        Returns:
            YAML config template as string.

        Raises:
            NotImplementedError: Method not yet implemented.
        """
        raise NotImplementedError
