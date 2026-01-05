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


class TestShorten:
    def test_unchanged_under_limit(self) -> None:
        assert StringOperator.shorten("short", 10, 2) == "short"

    def test_truncates_with_ellipsis(self) -> None:
        # prefix = text[:limit - suffix_length], ellipsis, suffix = text[-suffix_length:]
        assert StringOperator.shorten("hello world", 8, 2) == "hello ...ld"

    def test_exactly_at_limit(self) -> None:
        assert StringOperator.shorten("12345", 5, 1) == "12345"

    def test_one_over_limit(self) -> None:
        # prefix = text[:5-1] = text[:4] = "1234", suffix = text[-1] = "6"
        assert StringOperator.shorten("123456", 5, 1) == "1234...6"

    def test_preserves_suffix_length(self) -> None:
        # prefix = text[:7-3] = text[:4] = "abcd", suffix = text[-3:] = "hij"
        result = StringOperator.shorten("abcdefghij", 7, 3)
        assert result.endswith("hij")
        assert result == "abcd...hij"


class TestSlugify:
    def test_lowercases(self) -> None:
        assert StringOperator.slugify("Hello") == "hello"

    def test_replaces_spaces_with_hyphens(self) -> None:
        assert StringOperator.slugify("hello world") == "hello-world"

    def test_removes_unsafe_chars(self) -> None:
        # @ is in unsafe list, replaced with -
        assert StringOperator.slugify("hello@world") == "hello-world"

    def test_collapses_multiple_hyphens(self) -> None:
        assert StringOperator.slugify("hello---world") == "hello-world"

    def test_handles_multiple_spaces(self) -> None:
        assert StringOperator.slugify("hello   world") == "hello-world"

    def test_replaces_underscores(self) -> None:
        assert StringOperator.slugify("hello_world") == "hello-world"

    def test_complex_input(self) -> None:
        assert StringOperator.slugify("Foo Bar") == "foo-bar"


class TestPrepend:
    def test_adds_prefix_when_missing(self) -> None:
        assert StringOperator.prepend("bar", "pre-") == "pre-bar"

    def test_skips_existing_prefix(self) -> None:
        assert StringOperator.prepend("pre-bar", "pre-") == "pre-bar"

    def test_empty_text(self) -> None:
        assert StringOperator.prepend("", "pre-") == "pre-"

    def test_empty_prefix(self) -> None:
        assert StringOperator.prepend("bar", "") == "bar"


class TestCamelize:
    def test_underscore_to_pascal(self) -> None:
        assert StringOperator.camelize("first_name") == "FirstName"

    def test_hyphen_to_pascal(self) -> None:
        assert StringOperator.camelize("first-name") == "FirstName"

    def test_single_word(self) -> None:
        assert StringOperator.camelize("name") == "Name"

    def test_preserves_pascal_case(self) -> None:
        assert StringOperator.camelize("FirstName") == "FirstName"


class TestUnderscore:
    def test_pascal_to_snake(self) -> None:
        assert StringOperator.underscore("FirstName") == "first_name"

    def test_camel_to_snake(self) -> None:
        assert StringOperator.underscore("firstName") == "first_name"

    def test_single_word(self) -> None:
        assert StringOperator.underscore("Name") == "name"

    def test_already_snake(self) -> None:
        assert StringOperator.underscore("first_name") == "first_name"

    def test_acronym(self) -> None:
        assert StringOperator.underscore("HTMLParser") == "html_parser"


class TestHumanize:
    def test_snake_to_human(self) -> None:
        assert StringOperator.humanize("first_name") == "First name"

    def test_removes_id_suffix(self) -> None:
        assert StringOperator.humanize("user_id") == "User"

    def test_single_word(self) -> None:
        assert StringOperator.humanize("name") == "Name"


class TestPluralize:
    def test_regular_word(self) -> None:
        assert StringOperator.pluralize("cat") == "cats"

    def test_irregular_word(self) -> None:
        assert StringOperator.pluralize("mouse") == "mice"

    def test_minutes_exception(self) -> None:
        assert StringOperator.pluralize("minutes") == "minutes"


class TestSingularize:
    def test_regular_word(self) -> None:
        assert StringOperator.singularize("cats") == "cat"

    def test_irregular_word(self) -> None:
        assert StringOperator.singularize("mice") == "mouse"

    def test_minutes_exception(self) -> None:
        assert StringOperator.singularize("minutes") == "minutes"
