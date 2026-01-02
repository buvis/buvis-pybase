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
