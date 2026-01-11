"""Generate YAML config templates from pydantic settings classes."""

from __future__ import annotations

import types
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo, PydanticUndefined

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
    def _is_optional(field_info: FieldInfo) -> bool:
        """Check if field allows None.

        Args:
            field_info: Pydantic field info.

        Returns:
            True if field has None default or type includes None.
        """
        if field_info.default is None:
            return True
        annotation = field_info.annotation
        origin = get_origin(annotation)
        if origin in (Union, types.UnionType):
            return type(None) in get_args(annotation)
        return False

    @staticmethod
    def _is_required(field_info: FieldInfo) -> bool:
        """Check if field has no default.

        Args:
            field_info: Pydantic field info.

        Returns:
            True if field has no default value.
        """
        return (
            field_info.default is PydanticUndefined
            and field_info.default_factory is None
        )

    @staticmethod
    def _is_nested_model(annotation: Any) -> bool:
        """Check if annotation is a BaseModel subclass.

        Args:
            annotation: Type annotation.

        Returns:
            True if annotation is a BaseModel subclass.
        """
        origin = get_origin(annotation)
        if origin in (Union, types.UnionType):
            args = [a for a in get_args(annotation) if a is not type(None)]
            if len(args) == 1:
                return ConfigWriter._is_nested_model(args[0])
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return True
        return False

    @staticmethod
    def _extract_model_class(annotation: Any) -> type[BaseModel] | None:
        """Extract BaseModel class from annotation.

        Args:
            annotation: Type annotation.

        Returns:
            BaseModel subclass or None.
        """
        origin = get_origin(annotation)
        if origin in (Union, types.UnionType):
            args = [a for a in get_args(annotation) if a is not type(None)]
            if len(args) == 1:
                return ConfigWriter._extract_model_class(args[0])
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return annotation
        return None

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
