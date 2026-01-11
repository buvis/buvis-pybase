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


class TestConfigWriterStubs:
    """Tests for ConfigWriter stub methods."""

    def test_write_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            ConfigWriter.write(BaseModel, Path("test.yaml"), "test")  # type: ignore[arg-type]

    def test_generate_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            ConfigWriter.generate(BaseModel, "test")  # type: ignore[arg-type]
