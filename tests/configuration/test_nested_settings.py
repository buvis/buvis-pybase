"""Tests for nested pool settings examples."""

import pytest
from pydantic import ValidationError

from buvis.pybase.configuration.examples.nested_settings import (
    DatabaseSettings,
    PayrollSettings,
    PoolSettings,
)


class TestPoolSettingsDefaults:
    def test_min_and_max_size_defaults(self) -> None:
        pool = PoolSettings()

        assert pool.min_size == 5
        assert pool.max_size == 20


class TestDatabaseSettingsDefaults:
    def test_database_defaults(self) -> None:
        database = DatabaseSettings()

        assert database.url == ""
        assert isinstance(database.pool, PoolSettings)


class TestPayrollSettingsEnvNestedDelimiter:
    def test_nested_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUVIS_PAYROLL_DATABASE__POOL__MIN_SIZE", "10")

        settings = PayrollSettings()

        assert settings.database.pool.min_size == 10


class TestPayrollSettingsImmutable:
    def test_assignment_raises(self) -> None:
        settings = PayrollSettings()

        with pytest.raises(ValidationError):
            settings.database = DatabaseSettings(url="postgresql://immutable")
