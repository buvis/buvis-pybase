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
