"""Tests for JSON array parsing from environment variables."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from pydantic_settings.exceptions import SettingsError

from buvis.pybase.configuration.examples.complex_env_settings import (
    HCMSettings,
    PayrollSettings,
)


class TestJSONListParsing:
    def test_json_array_parsed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PRD test: JSON array -> list[PaymentRule]."""
        monkeypatch.setenv(
            "BUVIS_PAYROLL_PAYMENT_RULES",
            '[{"rule_id":"a","enabled":true}]',
        )

        settings = PayrollSettings()

        assert len(settings.payment_rules) == 1
        assert settings.payment_rules[0].rule_id == "a"
        assert settings.payment_rules[0].enabled is True

    def test_json_array_multiple_items(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Multiple items in JSON array are parsed."""
        monkeypatch.setenv(
            "BUVIS_PAYROLL_PAYMENT_RULES",
            '[{"rule_id":"a","enabled":true},{"rule_id":"b","enabled":false}]',
        )

        settings = PayrollSettings()

        assert len(settings.payment_rules) == 2
        assert settings.payment_rules[1].rule_id == "b"

    def test_empty_array(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PRD test: '[]' -> empty list."""
        monkeypatch.setenv("BUVIS_PAYROLL_PAYMENT_RULES", "[]")

        settings = PayrollSettings()

        assert settings.payment_rules == []

    def test_json_with_optional_field(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """JSON with optional bonus_pct field."""
        monkeypatch.setenv(
            "BUVIS_PAYROLL_PAYMENT_RULES",
            '[{"rule_id":"holiday","enabled":true,"bonus_pct":0.05}]',
        )

        settings = PayrollSettings()

        assert settings.payment_rules[0].bonus_pct == 0.05

    def test_default_empty_list(self) -> None:
        """Default payment_rules is empty list."""
        settings = PayrollSettings()

        assert settings.payment_rules == []


class TestPlainScalarParsing:
    def test_plain_scalar_still_works(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PRD test: Plain scalar 500 works for int fields."""
        monkeypatch.setenv("BUVIS_PAYROLL_BATCH_SIZE", "500")

        settings = PayrollSettings()

        assert settings.batch_size == 500

    def test_batch_size_default(self) -> None:
        """Default batch_size is 1000."""
        settings = PayrollSettings()

        assert settings.batch_size == 1000


class TestJSONParseErrors:
    """Tests for JSON parsing error handling."""

    def test_invalid_json_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PRD test: '[{broken' -> SettingsError with JSON parse error."""
        monkeypatch.setenv("BUVIS_PAYROLL_PAYMENT_RULES", "[{broken")

        with pytest.raises(SettingsError) as exc_info:
            PayrollSettings()

        error_str = str(exc_info.value).lower()
        assert "payment_rules" in error_str or "json" in error_str

    def test_wrong_type_in_json(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PRD test: rule_id:123 (wrong type) -> ValidationError."""
        monkeypatch.setenv(
            "BUVIS_PAYROLL_PAYMENT_RULES",
            '[{"rule_id":123,"enabled":true}]',
        )

        with pytest.raises(ValidationError) as exc_info:
            PayrollSettings()

        assert "rule_id" in str(exc_info.value)

    def test_missing_required_field(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PRD: Missing field -> ValidationError."""
        monkeypatch.setenv(
            "BUVIS_PAYROLL_PAYMENT_RULES",
            '[{"enabled":true}]',
        )

        with pytest.raises(ValidationError) as exc_info:
            PayrollSettings()

        assert "rule_id" in str(exc_info.value)


class TestHCMSettings:
    """Tests for HCMSettings dict parsing."""

    def test_headers_default_empty_dict(self) -> None:
        """Default headers is empty dict."""
        settings = HCMSettings()

        assert settings.headers == {}

    def test_api_url_default_empty(self) -> None:
        """Default api_url is empty string."""
        settings = HCMSettings()

        assert settings.api_url == ""

    def test_json_dict_parsing_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PRD test: JSON object -> dict[str, str]."""
        monkeypatch.setenv("BUVIS_HCM_HEADERS", '{"X-Api-Key":"test123"}')

        settings = HCMSettings()

        assert settings.headers == {"X-Api-Key": "test123"}

    def test_multiple_headers_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Multiple key-value pairs parse correctly."""
        headers_json = (
            '{"Authorization":"Bearer abc","X-Api-Key":"xyz",'
            '"Content-Type":"application/json"}'
        )
        monkeypatch.setenv("BUVIS_HCM_HEADERS", headers_json)

        settings = HCMSettings()

        assert settings.headers["Authorization"] == "Bearer abc"
        assert settings.headers["X-Api-Key"] == "xyz"
        assert settings.headers["Content-Type"] == "application/json"
        assert len(settings.headers) == 3

    def test_empty_dict_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PRD test: '{}' -> empty dict."""
        monkeypatch.setenv("BUVIS_HCM_HEADERS", "{}")

        settings = HCMSettings()

        assert settings.headers == {}

    def test_wrong_value_type_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """dict[str, str] rejects int value."""
        monkeypatch.setenv("BUVIS_HCM_HEADERS", '{"key":123}')

        with pytest.raises(ValidationError):
            HCMSettings()

    def test_immutable(self) -> None:
        """HCMSettings is frozen."""
        settings = HCMSettings()

        with pytest.raises(ValidationError):
            settings.api_url = "changed"
