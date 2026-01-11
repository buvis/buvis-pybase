"""Tests for ConfigWriter."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Union

import pytest
from pydantic import BaseModel

from buvis.pybase.configuration import ConfigWriter


class NestedModel(BaseModel):
    """Sample nested model for testing."""

    value: str


class TestFormatType:
    """Tests for ConfigWriter._format_type."""

    def test_literal_type(self) -> None:
        result = ConfigWriter._format_type(Literal["a", "b"])
        assert result == "one of: 'a', 'b'"

    def test_literal_single_value(self) -> None:
        result = ConfigWriter._format_type(Literal["DEBUG"])
        assert result == "one of: 'DEBUG'"

    def test_optional_str(self) -> None:
        result = ConfigWriter._format_type(str | None)
        assert result == "str | None (optional)"

    def test_optional_path(self) -> None:
        result = ConfigWriter._format_type(Path | None)
        assert result == "Path | None (optional)"

    def test_union_typing_module(self) -> None:
        result = ConfigWriter._format_type(Union[str, None])
        assert result == "str | None (optional)"

    def test_union_multiple_types(self) -> None:
        result = ConfigWriter._format_type(int | str)
        assert result == "int | str"

    def test_list_str(self) -> None:
        result = ConfigWriter._format_type(list[str])
        assert result == "list[str]"

    def test_dict_str_int(self) -> None:
        result = ConfigWriter._format_type(dict[str, int])
        assert result == "dict[str, int]"

    def test_list_path(self) -> None:
        result = ConfigWriter._format_type(list[Path])
        assert result == "list[Path]"

    def test_simple_str(self) -> None:
        result = ConfigWriter._format_type(str)
        assert result == "str"

    def test_simple_int(self) -> None:
        result = ConfigWriter._format_type(int)
        assert result == "int"

    def test_simple_bool(self) -> None:
        result = ConfigWriter._format_type(bool)
        assert result == "bool"

    def test_simple_path(self) -> None:
        result = ConfigWriter._format_type(Path)
        assert result == "Path"

    def test_basemodel_subclass(self) -> None:
        result = ConfigWriter._format_type(NestedModel)
        assert result == "NestedModel"

    def test_nested_generic(self) -> None:
        result = ConfigWriter._format_type(list[dict[str, int]])
        assert result == "list[dict[str, int]]"


class TestFormatValue:
    """Tests for ConfigWriter._format_value."""

    def test_none(self) -> None:
        assert ConfigWriter._format_value(None) == "null"

    def test_true(self) -> None:
        assert ConfigWriter._format_value(True) == "true"

    def test_false(self) -> None:
        assert ConfigWriter._format_value(False) == "false"

    def test_simple_string(self) -> None:
        assert ConfigWriter._format_value("simple") == "simple"

    def test_empty_string(self) -> None:
        assert ConfigWriter._format_value("") == '""'

    def test_string_with_colon(self) -> None:
        assert ConfigWriter._format_value("foo:bar") == '"foo:bar"'

    def test_string_with_hash(self) -> None:
        assert ConfigWriter._format_value("has#hash") == '"has#hash"'

    def test_path(self) -> None:
        assert ConfigWriter._format_value(Path("/tmp/test")) == "/tmp/test"

    def test_empty_list(self) -> None:
        assert ConfigWriter._format_value([]) == "[]"

    def test_list_strings(self) -> None:
        assert ConfigWriter._format_value(["a", "b"]) == "[a, b]"

    def test_list_with_null(self) -> None:
        assert ConfigWriter._format_value([1, None]) == "[1, null]"

    def test_empty_dict(self) -> None:
        assert ConfigWriter._format_value({}) == "{}"

    def test_dict_simple(self) -> None:
        assert ConfigWriter._format_value({"a": 1}) == "{a: 1}"

    def test_dict_with_bool(self) -> None:
        assert ConfigWriter._format_value({"x": True}) == "{x: true}"

    def test_int(self) -> None:
        assert ConfigWriter._format_value(42) == "42"

    def test_float(self) -> None:
        assert ConfigWriter._format_value(3.14) == "3.14"


class SampleSettings(BaseModel):
    """Sample settings for testing field analysis."""

    required_field: str
    optional_field: str | None = None
    optional_with_default: str = "default"
    nested: NestedModel | None = None
    nested_required: NestedModel
    list_field: list[str] = []


class TestIsOptional:
    """Tests for ConfigWriter._is_optional."""

    def test_field_with_none_default(self) -> None:
        field = SampleSettings.model_fields["optional_field"]
        assert ConfigWriter._is_optional(field) is True

    def test_field_with_string_default(self) -> None:
        field = SampleSettings.model_fields["optional_with_default"]
        assert ConfigWriter._is_optional(field) is False

    def test_required_field(self) -> None:
        field = SampleSettings.model_fields["required_field"]
        assert ConfigWriter._is_optional(field) is False

    def test_optional_nested_model(self) -> None:
        field = SampleSettings.model_fields["nested"]
        assert ConfigWriter._is_optional(field) is True


class TestIsRequired:
    """Tests for ConfigWriter._is_required."""

    def test_required_field(self) -> None:
        field = SampleSettings.model_fields["required_field"]
        assert ConfigWriter._is_required(field) is True

    def test_field_with_default(self) -> None:
        field = SampleSettings.model_fields["optional_with_default"]
        assert ConfigWriter._is_required(field) is False

    def test_field_with_none_default(self) -> None:
        field = SampleSettings.model_fields["optional_field"]
        assert ConfigWriter._is_required(field) is False

    def test_field_with_default_factory(self) -> None:
        field = SampleSettings.model_fields["list_field"]
        assert ConfigWriter._is_required(field) is False

    def test_nested_required(self) -> None:
        field = SampleSettings.model_fields["nested_required"]
        assert ConfigWriter._is_required(field) is True


class TestIsNestedModel:
    """Tests for ConfigWriter._is_nested_model."""

    def test_basemodel_subclass(self) -> None:
        assert ConfigWriter._is_nested_model(NestedModel) is True

    def test_optional_basemodel(self) -> None:
        assert ConfigWriter._is_nested_model(NestedModel | None) is True

    def test_string_type(self) -> None:
        assert ConfigWriter._is_nested_model(str) is False

    def test_list_type(self) -> None:
        assert ConfigWriter._is_nested_model(list[str]) is False


class TestExtractModelClass:
    """Tests for ConfigWriter._extract_model_class."""

    def test_direct_model(self) -> None:
        result = ConfigWriter._extract_model_class(NestedModel)
        assert result is NestedModel

    def test_optional_model(self) -> None:
        result = ConfigWriter._extract_model_class(NestedModel | None)
        assert result is NestedModel

    def test_non_model_returns_none(self) -> None:
        result = ConfigWriter._extract_model_class(str)
        assert result is None

    def test_list_returns_none(self) -> None:
        result = ConfigWriter._extract_model_class(list[str])
        assert result is None


class DatabaseSettings(BaseModel):
    """Sample database settings for nesting tests."""

    host: str = "localhost"
    port: int = 5432


class AppSettings(BaseModel):
    """Sample app settings with nested model."""

    name: str = "myapp"
    database: DatabaseSettings = DatabaseSettings()


class DeepSettings(BaseModel):
    """Settings with three-level nesting."""

    app: AppSettings = AppSettings()


class TestFormatNestedModel:
    """Tests for ConfigWriter._format_nested_model."""

    def test_flat_model_basic_types(self) -> None:
        result = ConfigWriter._format_nested_model(DatabaseSettings)
        assert "  host: localhost" in result
        assert "  port: 5432" in result

    def test_flat_model_preserves_order(self) -> None:
        result = ConfigWriter._format_nested_model(DatabaseSettings)
        lines = result.strip().split("\n")
        assert lines[0].strip().startswith("host")
        assert lines[1].strip().startswith("port")

    def test_nested_model_indentation(self) -> None:
        result = ConfigWriter._format_nested_model(AppSettings)
        assert "  name: myapp" in result
        assert "  database:" in result
        assert "    host: localhost" in result
        assert "    port: 5432" in result

    def test_required_field_empty_string(self) -> None:
        result = ConfigWriter._format_nested_model(SampleSettings)
        # required_field has no default, should get empty string
        assert "  required_field: " in result

    def test_default_factory_list(self) -> None:
        result = ConfigWriter._format_nested_model(SampleSettings)
        assert "  list_field: []" in result

    def test_three_level_nesting(self) -> None:
        result = ConfigWriter._format_nested_model(DeepSettings)
        assert "  app:" in result
        assert "    name: myapp" in result
        assert "    database:" in result
        assert "      host: localhost" in result
        assert "      port: 5432" in result

    def test_custom_indent(self) -> None:
        result = ConfigWriter._format_nested_model(DatabaseSettings, indent=4)
        assert "    host: localhost" in result
        assert "    port: 5432" in result


class TestConfigWriterStubs:
    """Tests for ConfigWriter stub methods."""

    def test_write_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            ConfigWriter.write(BaseModel, Path("test.yaml"), "test")  # type: ignore[arg-type]

    def test_generate_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            ConfigWriter.generate(BaseModel, "test")  # type: ignore[arg-type]
