from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["JiraFieldMappings", "JiraSettings"]


class JiraFieldMappings(BaseModel):
    """Custom field ID mappings for JIRA instance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    ticket: str = "customfield_11502"
    team: str = "customfield_10501"
    feature: str = "customfield_10001"
    region: str = "customfield_12900"


class JiraSettings(BaseSettings):
    """JIRA adapter configuration.

    Loads from env vars with BUVIS_JIRA_ prefix.
    Nested delimiter: __ (e.g., BUVIS_JIRA__FIELD_MAPPINGS__TICKET).
    """

    model_config = SettingsConfigDict(
        env_prefix="BUVIS_JIRA_",
        env_nested_delimiter="__",
        frozen=True,
        extra="forbid",
    )

    server: str
    token: str
    proxy: str | None = None
    field_mappings: JiraFieldMappings = JiraFieldMappings()
