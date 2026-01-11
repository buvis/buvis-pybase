"""Generate YAML config templates from pydantic settings classes."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Union, get_args, get_origin

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
    def _format_type(annotation: Any) -> str:
        """Format type annotation for YAML comment.

        Args:
            annotation: Type annotation to format.

        Returns:
            Human-readable type string.
        """
        origin = get_origin(annotation)

        # Handle Literal["a", "b"] -> "one of: 'a', 'b'"
        if origin is Literal:
            values = get_args(annotation)
            formatted = ", ".join(f"'{v}'" for v in values)
            return f"one of: {formatted}"

        # Handle Optional/Union (X | None)
        if origin is Union:
            args = get_args(annotation)
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1 and type(None) in args:
                inner = ConfigWriter._format_type(non_none[0])
                return f"{inner} | None (optional)"
            return " | ".join(ConfigWriter._format_type(a) for a in args)

        # Handle generic types like list[str], dict[str, int]
        if origin is not None:
            args = get_args(annotation)
            if args:
                formatted_args = ", ".join(ConfigWriter._format_type(a) for a in args)
                return f"{origin.__name__}[{formatted_args}]"
            return origin.__name__

        # Simple types: str, int, bool, Path, BaseModel subclass
        if hasattr(annotation, "__name__"):
            return annotation.__name__
        return str(annotation)

    @staticmethod
    def _format_value(value: Any) -> str:
        """Format value for YAML output.

        Args:
            value: Value to format.

        Returns:
            YAML-formatted value string.
        """
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            # Quote strings with special chars or if empty
            if not value or any(c in value for c in ":{}[]#&*!|>'\"%@`"):
                return f'"{value}"'
            return value
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, (list, tuple)):
            if not value:
                return "[]"
            items = ", ".join(ConfigWriter._format_value(v) for v in value)
            return f"[{items}]"
        if isinstance(value, dict):
            if not value:
                return "{}"
            items = ", ".join(
                f"{k}: {ConfigWriter._format_value(v)}" for k, v in value.items()
            )
            return "{" + items + "}"
        return str(value)

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
