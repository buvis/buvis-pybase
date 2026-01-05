from __future__ import annotations

from buvis.pybase.formatting.string_operator.string_case_tools import StringCaseTools


class TestHumanize:
    def test_converts_underscore_to_spaces(self) -> None:
        result = StringCaseTools.humanize("user_name")
        assert result == "User name"

    def test_handles_multiple_underscores(self) -> None:
        result = StringCaseTools.humanize("first_middle_last")
        assert result == "First middle last"

    def test_handles_single_word(self) -> None:
        result = StringCaseTools.humanize("name")
        assert result == "Name"

    def test_handles_id_suffix(self) -> None:
        # inflection removes trailing _id
        result = StringCaseTools.humanize("user_id")
        assert result == "User"


class TestUnderscore:
    def test_converts_pascal_case(self) -> None:
        result = StringCaseTools.underscore("SomeValue")
        assert result == "some_value"

    def test_converts_camel_case(self) -> None:
        result = StringCaseTools.underscore("someValue")
        assert result == "some_value"

    def test_handles_already_underscored(self) -> None:
        result = StringCaseTools.underscore("some_value")
        assert result == "some_value"

    def test_handles_consecutive_caps(self) -> None:
        result = StringCaseTools.underscore("HTMLParser")
        assert result == "html_parser"


class TestAsNoteFieldName:
    def test_converts_pascal_case_to_kebab(self) -> None:
        result = StringCaseTools.as_note_field_name("SomeValue")
        assert result == "some-value"

    def test_converts_camel_case_to_kebab(self) -> None:
        result = StringCaseTools.as_note_field_name("someValue")
        assert result == "some-value"

    def test_handles_already_kebab_case(self) -> None:
        result = StringCaseTools.as_note_field_name("some-value")
        assert result == "some-value"

    def test_lowercases_result(self) -> None:
        result = StringCaseTools.as_note_field_name("SOME_VALUE")
        assert result == "some-value"
