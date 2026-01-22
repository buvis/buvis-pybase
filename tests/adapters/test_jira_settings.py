from __future__ import annotations

from pydantic import ValidationError
import pytest

from buvis.pybase.adapters.jira.settings import JiraFieldMappings, JiraSettings


def test_field_mappings_defaults() -> None:
    """Field mappings use the expected custom field IDs."""
    mappings = JiraFieldMappings()

    assert mappings.ticket == "customfield_11502"
    assert mappings.team == "customfield_10501"
    assert mappings.feature == "customfield_10001"
    assert mappings.region == "customfield_12900"


def test_settings_load_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """JiraSettings picks up server and token from env vars."""
    monkeypatch.setenv("BUVIS_JIRA_SERVER", "https://jira.example")
    monkeypatch.setenv("BUVIS_JIRA_TOKEN", "token-value")

    settings = JiraSettings()

    assert settings.server == "https://jira.example"
    assert settings.token == "token-value"
    assert settings.proxy is None
    assert settings.field_mappings.ticket == "customfield_11502"


def test_nested_field_mappings_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Nested env var overrides field mappings for ticket."""
    monkeypatch.setenv("BUVIS_JIRA_SERVER", "https://jira.example")
    monkeypatch.setenv("BUVIS_JIRA_TOKEN", "token-value")
    monkeypatch.setenv("BUVIS_JIRA_FIELD_MAPPINGS__TICKET", "customfield_99999")

    settings = JiraSettings()

    assert settings.field_mappings.ticket == "customfield_99999"


def test_proxy_defaults_to_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Proxy field defaults to None when unset."""
    monkeypatch.setenv("BUVIS_JIRA_SERVER", "https://jira.example")
    monkeypatch.setenv("BUVIS_JIRA_TOKEN", "token-value")

    settings = JiraSettings()

    assert settings.proxy is None


def test_settings_frozen_rejects_mutation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Frozen models cannot be modified after creation."""
    monkeypatch.setenv("BUVIS_JIRA_SERVER", "https://jira.example")
    monkeypatch.setenv("BUVIS_JIRA_TOKEN", "token-value")

    settings = JiraSettings()

    with pytest.raises(ValidationError):
        settings.server = "https://changed.example"


def test_extra_forbid_rejects_unknown_fields() -> None:
    """Passing an unknown field raises a validation error."""
    with pytest.raises(ValidationError):
        JiraSettings(server="https://jira.example", token="token", bogus="value")  # type: ignore[arg-type]
