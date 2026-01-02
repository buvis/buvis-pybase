from __future__ import annotations

import pytest
from pydantic import ValidationError

from buvis.pybase.configuration import BuvisSettings


class TestBuvisSettingsDefaults:
    def test_defaults(self) -> None:
        settings = BuvisSettings()

        assert settings.debug is False
        assert settings.log_level == "INFO"


class TestBuvisSettingsEnvLoading:
    def test_env_loading(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUVIS_DEBUG", "true")

        settings = BuvisSettings()

        assert settings.debug is True


class TestLogLevelValidation:
    @pytest.mark.parametrize(
        "level",
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    def test_valid_log_levels(
        self, level: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("BUVIS_LOG_LEVEL", level)

        settings = BuvisSettings()

        assert settings.log_level == level

    def test_invalid_log_level_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from pydantic import ValidationError

        monkeypatch.setenv("BUVIS_LOG_LEVEL", "TRACE")

        with pytest.raises(ValidationError):
            BuvisSettings()

    def test_lowercase_env_name_accepted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """case_sensitive=False means env var NAME is case-insensitive."""
        monkeypatch.setenv("buvis_log_level", "DEBUG")

        settings = BuvisSettings()

        assert settings.log_level == "DEBUG"


class TestCaseInsensitiveEnvLoading:
    def test_uppercase_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUVIS_DEBUG", "true")

        settings = BuvisSettings()

        assert settings.debug is True

    def test_lowercase_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("buvis_debug", "true")

        settings = BuvisSettings()

        assert settings.debug is True

    def test_mixed_case_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("Buvis_Debug", "true")

        settings = BuvisSettings()

        assert settings.debug is True


class TestBuvisSettingsImmutability:
    def test_immutable(self) -> None:
        settings = BuvisSettings()

        with pytest.raises(ValidationError):
            settings.debug = True  # type: ignore[attr-defined]


class TestBuvisSettingsExtraForbid:
    def test_unknown_field_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            BuvisSettings(extra_field=True)  # type: ignore[arg-type]


class TestValidateToolName:
    def test_valid_uppercase(self) -> None:
        from buvis.pybase.configuration import validate_tool_name

        validate_tool_name("PAYROLL")  # Should not raise

    def test_valid_with_underscore(self) -> None:
        from buvis.pybase.configuration import validate_tool_name

        validate_tool_name("USER_AUTH")  # Should not raise

    def test_hyphen_raises(self) -> None:
        from buvis.pybase.configuration import validate_tool_name

        with pytest.raises(ValueError, match="SCREAMING_SNAKE_CASE"):
            validate_tool_name("PAY-ROLL")

    def test_lowercase_raises(self) -> None:
        from buvis.pybase.configuration import validate_tool_name

        with pytest.raises(ValueError, match="SCREAMING_SNAKE_CASE"):
            validate_tool_name("payroll")

    def test_mixed_case_raises(self) -> None:
        from buvis.pybase.configuration import validate_tool_name

        with pytest.raises(ValueError, match="SCREAMING_SNAKE_CASE"):
            validate_tool_name("Payroll")


class TestCreateToolSettingsClass:
    def test_creates_class_with_correct_prefix(self) -> None:
        from buvis.pybase.configuration import create_tool_settings_class

        Settings = create_tool_settings_class("PAYROLL", batch_size=(int, 1000))

        assert Settings.model_config["env_prefix"] == "BUVIS_PAYROLL_"

    def test_loads_env_var_with_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from buvis.pybase.configuration import create_tool_settings_class

        monkeypatch.setenv("BUVIS_PAYROLL_BATCH_SIZE", "500")
        Settings = create_tool_settings_class("PAYROLL", batch_size=(int, 1000))

        settings = Settings()

        assert settings.batch_size == 500

    def test_default_value_used(self) -> None:
        from buvis.pybase.configuration import create_tool_settings_class

        Settings = create_tool_settings_class("PAYROLL", batch_size=(int, 1000))

        settings = Settings()

        assert settings.batch_size == 1000

    def test_hyphen_in_tool_name_raises(self) -> None:
        from buvis.pybase.configuration import create_tool_settings_class

        with pytest.raises(ValueError, match="SCREAMING_SNAKE_CASE"):
            create_tool_settings_class("PAY-ROLL", batch_size=(int, 1000))

    def test_lowercase_tool_name_raises(self) -> None:
        from buvis.pybase.configuration import create_tool_settings_class

        with pytest.raises(ValueError):
            create_tool_settings_class("payroll", batch_size=(int, 1000))

    def test_class_name_formatting(self) -> None:
        from buvis.pybase.configuration import create_tool_settings_class

        Settings = create_tool_settings_class("USER_AUTH")

        assert Settings.__name__ == "UserAuthSettings"

    def test_frozen_and_extra_forbid(self) -> None:
        from buvis.pybase.configuration import create_tool_settings_class

        Settings = create_tool_settings_class("PAYROLL")

        assert Settings.model_config["frozen"] is True
        assert Settings.model_config["extra"] == "forbid"

    def test_multiple_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from buvis.pybase.configuration import create_tool_settings_class

        monkeypatch.setenv("BUVIS_MYAPP_DEBUG", "true")
        Settings = create_tool_settings_class(
            "MYAPP",
            debug=(bool, False),
            timeout=(int, 30),
        )

        settings = Settings()

        assert settings.debug is True
        assert settings.timeout == 30


class TestValidateEnvVarName:
    @pytest.mark.parametrize(
        "name",
        [
            "BUVIS_DEBUG",
            "BUVIS_PAYROLL_BATCH_SIZE",
            "BUVIS_HCM_API_URL",
            "BUVIS_A",
            "BUVIS_A1",
            "BUVIS_TEST_123",
        ],
    )
    def test_valid_names(self, name: str) -> None:
        from buvis.pybase.configuration import validate_env_var_name

        assert validate_env_var_name(name) is True

    @pytest.mark.parametrize(
        "name",
        [
            "DEBUG",  # no prefix
            "buvis_debug",  # lowercase
            "BUVIS-DEBUG",  # hyphen
            "BUVIS_",  # empty field
            "",  # empty string
            "BUVIS_123",  # starts with number after prefix
            "BUVIS_debug",  # lowercase after prefix
            "OTHER_DEBUG",  # wrong prefix
        ],
    )
    def test_invalid_names(self, name: str) -> None:
        from buvis.pybase.configuration import validate_env_var_name

        assert validate_env_var_name(name) is False


class TestPrefixRequired:
    """Security tests: env vars without BUVIS_ prefix are ignored."""

    def test_unprefixed_debug_ignored(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DEBUG=true without BUVIS_ prefix must not affect settings."""
        monkeypatch.delenv("BUVIS_DEBUG", raising=False)
        monkeypatch.setenv("DEBUG", "true")

        settings = BuvisSettings()

        assert settings.debug is False  # Uses default, ignores DEBUG

    def test_tool_without_buvis_prefix_ignored(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PAYROLL_BATCH_SIZE without BUVIS_PAYROLL_ prefix must be ignored."""
        from buvis.pybase.configuration import create_tool_settings_class

        monkeypatch.delenv("BUVIS_PAYROLL_BATCH_SIZE", raising=False)
        monkeypatch.setenv("PAYROLL_BATCH_SIZE", "500")

        Settings = create_tool_settings_class("PAYROLL", batch_size=(int, 1000))
        settings = Settings()

        assert settings.batch_size == 1000  # Uses default


class TestAssertValidEnvVarName:
    def test_valid_name_no_exception(self) -> None:
        from buvis.pybase.configuration import assert_valid_env_var_name

        assert_valid_env_var_name("BUVIS_DEBUG")  # Should not raise

    def test_invalid_name_raises_valueerror(self) -> None:
        from buvis.pybase.configuration import assert_valid_env_var_name

        with pytest.raises(ValueError, match="Invalid env var name"):
            assert_valid_env_var_name("debug")

    def test_error_message_contains_name(self) -> None:
        from buvis.pybase.configuration import assert_valid_env_var_name

        with pytest.raises(ValueError, match="bad_name"):
            assert_valid_env_var_name("bad_name")

    def test_error_message_contains_format_hint(self) -> None:
        from buvis.pybase.configuration import assert_valid_env_var_name

        with pytest.raises(ValueError, match="SCREAMING_SNAKE_CASE"):
            assert_valid_env_var_name("invalid")
