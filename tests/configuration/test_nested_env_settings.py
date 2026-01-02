"""Tests for nested env var resolution with __ delimiter."""

from __future__ import annotations

import pytest

from buvis.pybase.configuration.examples.nested_settings import PayrollSettings


class TestNestedEnvResolution:
    def test_nested_pool_min_size(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PRD test: __ correctly descends into nested model."""
        monkeypatch.setenv("BUVIS_PAYROLL_DATABASE__POOL__MIN_SIZE", "10")

        settings = PayrollSettings()

        assert settings.database.pool.min_size == 10

    def test_nested_pool_max_size(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUVIS_PAYROLL_DATABASE__POOL__MAX_SIZE", "50")

        settings = PayrollSettings()

        assert settings.database.pool.max_size == 50

    def test_multiple_nested_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUVIS_PAYROLL_DATABASE__POOL__MIN_SIZE", "10")
        monkeypatch.setenv("BUVIS_PAYROLL_DATABASE__POOL__MAX_SIZE", "100")

        settings = PayrollSettings()

        assert settings.database.pool.min_size == 10
        assert settings.database.pool.max_size == 100

    def test_nested_database_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUVIS_PAYROLL_DATABASE__URL", "postgres://localhost/db")

        settings = PayrollSettings()

        assert settings.database.url == "postgres://localhost/db"

    def test_defaults_without_env_vars(self) -> None:
        settings = PayrollSettings()

        assert settings.database.pool.min_size == 5
        assert settings.database.pool.max_size == 20
        assert settings.database.url == ""


class TestMixedEnvResolution:
    """Tests for combining direct and nested env vars."""

    def test_mixed_database_and_pool(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Both database url and nested pool settings work together."""
        monkeypatch.setenv("BUVIS_PAYROLL_DATABASE__URL", "postgres://host/db")
        monkeypatch.setenv("BUVIS_PAYROLL_DATABASE__POOL__MIN_SIZE", "15")

        settings = PayrollSettings()

        assert settings.database.url == "postgres://host/db"
        assert settings.database.pool.min_size == 15

    def test_single_underscore_does_not_work(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Single underscore in nested path is not recognized.

        Pydantic-settings requires __ delimiter for nested models.
        BUVIS_PAYROLL_DATABASE_URL doesn't work; use DATABASE__URL.
        """
        monkeypatch.setenv("BUVIS_PAYROLL_DATABASE_URL", "should-not-work")

        settings = PayrollSettings()

        assert settings.database.url == ""  # Default, env var not matched
