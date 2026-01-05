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
