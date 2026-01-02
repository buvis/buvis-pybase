"""Tests for settings immutability enforcement."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from buvis.pybase.configuration.settings import GlobalSettings, ToolSettings


class TestGlobalSettingsImmutability:
    """Tests for GlobalSettings frozen behavior."""

    def test_debug_immutable(self) -> None:
        """debug field cannot be mutated."""
        settings = GlobalSettings()

        with pytest.raises(ValidationError):
            settings.debug = True

    def test_log_level_immutable(self) -> None:
        """log_level field cannot be mutated."""
        settings = GlobalSettings()

        with pytest.raises(ValidationError):
            settings.log_level = "DEBUG"

    def test_output_format_immutable(self) -> None:
        """output_format field cannot be mutated."""
        settings = GlobalSettings()

        with pytest.raises(ValidationError):
            settings.output_format = "json"


class TestToolSettingsImmutability:
    """Tests for ToolSettings frozen behavior."""

    def test_enabled_immutable(self) -> None:
        """enabled field cannot be mutated."""
        tool = ToolSettings()

        with pytest.raises(ValidationError):
            tool.enabled = False


class TestImmutabilityErrorMessages:
    """Tests for error message content on mutation attempts."""

    def test_error_mentions_frozen(self) -> None:
        """Mutation error mentions frozen or immutable."""
        settings = GlobalSettings()

        with pytest.raises(ValidationError) as exc_info:
            settings.debug = True

        error_str = str(exc_info.value).lower()
        assert "frozen" in error_str or "immutable" in error_str

    def test_error_mentions_field_name(self) -> None:
        """Mutation error mentions the field name."""
        settings = GlobalSettings()

        with pytest.raises(ValidationError) as exc_info:
            settings.log_level = "ERROR"

        assert "log_level" in str(exc_info.value)
