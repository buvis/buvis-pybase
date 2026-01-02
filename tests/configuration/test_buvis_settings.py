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
