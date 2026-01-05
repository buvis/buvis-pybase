from __future__ import annotations

from buvis.pybase.formatting.string_operator.string_operator import StringOperator


class TestCollapse:
    def test_collapses_multiple_spaces(self) -> None:
        assert StringOperator.collapse("hello   world") == "hello world"

    def test_strips_leading_trailing(self) -> None:
        assert StringOperator.collapse("  hello  ") == "hello"

    def test_handles_tabs_and_newlines(self) -> None:
        assert StringOperator.collapse("hello\t\nworld") == "hello world"

    def test_empty_string(self) -> None:
        assert StringOperator.collapse("") == ""

    def test_only_whitespace(self) -> None:
        assert StringOperator.collapse("   \t\n  ") == ""
