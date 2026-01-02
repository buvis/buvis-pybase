"""Tests for payment rule JSON env parsing example."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from buvis.pybase.configuration.examples import PaymentRule, PayrollSettings


class TestPaymentRule:
    def test_defaults(self) -> None:
        rule = PaymentRule(rule_id="standard", enabled=True)

        assert rule.bonus_pct is None
        assert rule.enabled is True

    def test_validation_error_for_invalid_bonus(self) -> None:
        with pytest.raises(ValidationError):
            PaymentRule(rule_id="bad", enabled=True, bonus_pct="nope")  # type: ignore[arg-type]


class TestPayrollSettings:
    def test_defaults(self) -> None:
        settings = PayrollSettings()

        assert settings.payment_rules == []
        assert settings.batch_size == 1000

    def test_json_list_parsing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rules = [
            {"rule_id": "holiday", "enabled": True, "bonus_pct": 0.05},
            {"rule_id": "waiver", "enabled": False},
        ]
        monkeypatch.setenv("BUVIS_PAYROLL_PAYMENT_RULES", json.dumps(rules))

        settings = PayrollSettings()

        assert len(settings.payment_rules) == 2
        assert settings.payment_rules[0].bonus_pct == 0.05
        assert settings.payment_rules[1].enabled is False

    def test_batch_size_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUVIS_PAYROLL_BATCH_SIZE", "250")

        settings = PayrollSettings()

        assert settings.batch_size == 250

    def test_immutability(self) -> None:
        settings = PayrollSettings()

        with pytest.raises(ValidationError):
            settings.payment_rules = []
