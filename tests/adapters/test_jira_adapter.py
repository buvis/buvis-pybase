from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO
from buvis.pybase.adapters.jira.jira import JiraAdapter
from buvis.pybase.adapters.jira.exceptions import JiraNotFoundError
from buvis.pybase.adapters.jira.settings import JiraFieldMappings, JiraSettings
from jira.exceptions import JIRAError


@pytest.fixture
def jira_settings(monkeypatch: pytest.MonkeyPatch) -> JiraSettings:
    """Create JiraSettings instance sourced from environment variables."""
    monkeypatch.setenv("BUVIS_JIRA_SERVER", "https://jira.example.com")
    monkeypatch.setenv("BUVIS_JIRA_TOKEN", "test-token")
    return JiraSettings()


@pytest.fixture
def sample_issue_dto() -> JiraIssueDTO:
    """Create a sample JiraIssueDTO for testing."""
    return JiraIssueDTO(
        project="PROJ",
        title="Test Issue",
        description="Test description",
        issue_type="Task",
        labels=["test", "automated"],
        priority="Medium",
        ticket="PARENT-123",
        feature="EPIC-456",
        assignee="testuser",
        reporter="reporter",
        team="DevTeam",
        region="US",
    )


class TestJiraAdapterInit:
    """Test JiraAdapter initialization."""

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_creates_client_with_server_and_token(
        self, mock_jira: MagicMock, jira_settings: JiraSettings
    ) -> None:
        """Valid settings create a JIRA client."""
        JiraAdapter(jira_settings)

        mock_jira.assert_called_once_with(
            server="https://jira.example.com",
            token_auth="test-token",
        )

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_sets_proxy_when_configured(
        self, mock_jira: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Proxy config sets https_proxy env var and clears existing ones."""
        monkeypatch.setenv("https_proxy", "old")
        monkeypatch.setenv("http_proxy", "old")
        monkeypatch.setenv("BUVIS_JIRA_SERVER", "https://jira.example.com")
        monkeypatch.setenv("BUVIS_JIRA_TOKEN", "test-token")
        monkeypatch.setenv("BUVIS_JIRA_PROXY", "http://proxy.example.com:8080")

        JiraAdapter(JiraSettings())

        assert os.environ.get("https_proxy") == "http://proxy.example.com:8080"
        assert "http_proxy" not in os.environ


class TestJiraAdapterCreate:
    """Test JiraAdapter.create() method."""

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_creates_issue_with_correct_fields(
        self,
        mock_jira_cls: MagicMock,
        jira_settings: JiraSettings,
        sample_issue_dto: JiraIssueDTO,
    ) -> None:
        """create() passes correct field mapping to JIRA API."""
        mock_jira = mock_jira_cls.return_value
        mock_issue = MagicMock()
        mock_issue.key = "PROJ-123"
        mock_issue.permalink.return_value = "https://jira.example.com/browse/PROJ-123"
        mock_issue.fields.project.key = "PROJ"
        mock_issue.fields.summary = "Test Issue"
        mock_issue.fields.description = "Test description"
        mock_issue.fields.issuetype.name = "Task"
        mock_issue.fields.labels = ["test", "automated"]
        mock_issue.fields.priority.name = "Medium"
        mock_issue.fields.customfield_11502 = "PARENT-123"
        mock_issue.fields.customfield_10001 = "EPIC-456"
        mock_issue.fields.assignee.key = "testuser"
        mock_issue.fields.reporter.key = "reporter"
        mock_issue.fields.customfield_10501.value = "DevTeam"
        mock_issue.fields.customfield_12900.value = "US"
        mock_jira.create_issue.return_value = mock_issue
        mock_jira.issue.return_value = mock_issue

        adapter = JiraAdapter(jira_settings)
        adapter.create(sample_issue_dto)

        mock_jira.create_issue.assert_called_once()
        call_fields = mock_jira.create_issue.call_args[1]["fields"]
        assert call_fields["project"] == {"key": "PROJ"}
        assert call_fields["summary"] == "Test Issue"
        assert call_fields["assignee"] == {"key": "testuser", "name": "testuser"}
        field_mappings = jira_settings.field_mappings
        assert call_fields[field_mappings.team] == {"value": "DevTeam"}

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_returns_dto_with_id_and_link(
        self,
        mock_jira_cls: MagicMock,
        jira_settings: JiraSettings,
        sample_issue_dto: JiraIssueDTO,
    ) -> None:
        """create() returns DTO with id and link populated."""
        mock_jira = mock_jira_cls.return_value
        mock_issue = MagicMock()
        mock_issue.key = "PROJ-999"
        mock_issue.permalink.return_value = "https://jira.example.com/browse/PROJ-999"
        mock_issue.fields.project.key = "PROJ"
        mock_issue.fields.summary = "Test Issue"
        mock_issue.fields.description = "Test description"
        mock_issue.fields.issuetype.name = "Task"
        mock_issue.fields.labels = ["test", "automated"]
        mock_issue.fields.priority.name = "Medium"
        mock_issue.fields.customfield_11502 = "PARENT-123"
        mock_issue.fields.customfield_10001 = "EPIC-456"
        mock_issue.fields.assignee.key = "testuser"
        mock_issue.fields.reporter.key = "reporter"
        mock_issue.fields.customfield_10501.value = "DevTeam"
        mock_issue.fields.customfield_12900.value = "US"
        mock_jira.create_issue.return_value = mock_issue
        mock_jira.issue.return_value = mock_issue

        adapter = JiraAdapter(jira_settings)
        result = adapter.create(sample_issue_dto)

        assert result.id == "PROJ-999"
        assert result.link == "https://jira.example.com/browse/PROJ-999"
        assert isinstance(result, JiraIssueDTO)

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_updates_custom_fields_after_creation(
        self,
        mock_jira_cls: MagicMock,
        jira_settings: JiraSettings,
        sample_issue_dto: JiraIssueDTO,
    ) -> None:
        """create() updates custom fields that require post-creation update."""
        mock_jira = mock_jira_cls.return_value
        mock_created_issue = MagicMock()
        mock_created_issue.key = "PROJ-123"
        mock_fetched_issue = MagicMock()
        mock_fetched_issue.key = "PROJ-123"
        mock_fetched_issue.permalink.return_value = (
            "https://jira.example.com/browse/PROJ-123"
        )
        mock_fetched_issue.fields.project.key = "PROJ"
        mock_fetched_issue.fields.summary = "Test Issue"
        mock_fetched_issue.fields.description = "Test description"
        mock_fetched_issue.fields.issuetype.name = "Task"
        mock_fetched_issue.fields.labels = ["test", "automated"]
        mock_fetched_issue.fields.priority.name = "Medium"
        mock_fetched_issue.fields.customfield_11502 = "PARENT-123"
        mock_fetched_issue.fields.customfield_10001 = "EPIC-456"
        mock_fetched_issue.fields.assignee.key = "testuser"
        mock_fetched_issue.fields.reporter.key = "reporter"
        mock_fetched_issue.fields.customfield_10501.value = "DevTeam"
        mock_fetched_issue.fields.customfield_12900.value = "US"
        mock_jira.create_issue.return_value = mock_created_issue
        mock_jira.issue.return_value = mock_fetched_issue

        adapter = JiraAdapter(jira_settings)
        adapter.create(sample_issue_dto)

        mock_jira.issue.assert_called_once_with("PROJ-123")
        assert mock_fetched_issue.update.call_count == 2
        field_mappings = jira_settings.field_mappings
        mock_fetched_issue.update.assert_any_call(
            **{field_mappings.feature: "EPIC-456"}
        )
        mock_fetched_issue.update.assert_any_call(
            **{field_mappings.region: {"value": "US"}}
        )


class TestJiraAdapterGet:
    """Test JiraAdapter.get() method."""

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_returns_dto_for_valid_key(
        self, mock_jira_cls: MagicMock, jira_settings: JiraSettings
    ) -> None:
        """get() returns a populated DTO when Jira returns an issue."""
        mock_jira = mock_jira_cls.return_value
        mock_issue = MagicMock()
        mock_issue.key = "PROJ-1"
        mock_issue.permalink.return_value = "https://jira.example.com/browse/PROJ-1"
        mock_issue.fields.project.key = "PROJ"
        mock_issue.fields.summary = "Loaded issue"
        mock_issue.fields.description = "Loaded description"
        mock_issue.fields.issuetype.name = "Task"
        mock_issue.fields.labels = ["loaded"]
        priority_field = MagicMock()
        priority_field.name = "High"
        mock_issue.fields.priority = priority_field
        mock_issue.fields.customfield_11502 = "PARENT-123"
        mock_issue.fields.customfield_10001 = "EPIC-456"
        mock_issue.fields.assignee.key = "testuser"
        mock_issue.fields.reporter.key = "reporter"
        mock_issue.fields.customfield_10501.value = "DevTeam"
        mock_issue.fields.customfield_12900.value = "US"
        mock_jira.issue.return_value = mock_issue

        adapter = JiraAdapter(jira_settings)
        result = adapter.get("PROJ-1")

        assert isinstance(result, JiraIssueDTO)
        assert result.id == "PROJ-1"
        assert result.link == "https://jira.example.com/browse/PROJ-1"
        assert result.ticket == "PARENT-123"
        assert result.feature == "EPIC-456"
        assert result.team == "DevTeam"
        assert result.region == "US"

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_raises_not_found_for_404(
        self, mock_jira_cls: MagicMock, jira_settings: JiraSettings
    ) -> None:
        """A 404 from Jira is wrapped in JiraNotFoundError."""
        mock_jira = mock_jira_cls.return_value
        error = JIRAError("not found")
        error.status_code = 404
        mock_jira.issue.side_effect = error

        adapter = JiraAdapter(jira_settings)
        with pytest.raises(JiraNotFoundError):
            adapter.get("PROJ-404")

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_propagates_other_jira_errors(
        self, mock_jira_cls: MagicMock, jira_settings: JiraSettings
    ) -> None:
        """Non-404 errors bubble up unchanged."""
        mock_jira = mock_jira_cls.return_value
        error = JIRAError("server error")
        error.status_code = 500
        mock_jira.issue.side_effect = error

        adapter = JiraAdapter(jira_settings)
        with pytest.raises(JIRAError):
            adapter.get("PROJ-500")

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_uses_field_mappings_from_settings(self, mock_jira_cls: MagicMock) -> None:
        """Custom field mappings are respected when reading Jira fields."""
        mock_jira = mock_jira_cls.return_value
        custom_field_mappings = JiraFieldMappings(
            ticket="custom_ticket",
            feature="custom_feature",
            team="custom_team",
            region="custom_region",
        )
        settings = JiraSettings(
            server="https://jira.example.com",
            token="test-token",
            field_mappings=custom_field_mappings,
        )
        mock_issue = MagicMock()
        mock_issue.key = "PROJ-2"
        mock_issue.permalink.return_value = "https://jira.example.com/browse/PROJ-2"
        mock_issue.fields.project.key = "PROJ"
        mock_issue.fields.summary = "Custom mapping issue"
        mock_issue.fields.description = "Custom description"
        mock_issue.fields.issuetype.name = "Bug"
        mock_issue.fields.labels = []
        priority_field = MagicMock()
        priority_field.name = "Medium"
        mock_issue.fields.priority = priority_field
        setattr(mock_issue.fields, "custom_ticket", "CUSTOM-123")
        setattr(mock_issue.fields, "custom_feature", "FEATURE-123")
        team_field = MagicMock()
        team_field.value = "CustomTeam"
        setattr(mock_issue.fields, "custom_team", team_field)
        region_field = MagicMock()
        region_field.value = "CustomRegion"
        setattr(mock_issue.fields, "custom_region", region_field)
        mock_issue.fields.assignee.key = "assignee"
        mock_issue.fields.reporter.key = "reporter"
        mock_jira.issue.return_value = mock_issue

        adapter = JiraAdapter(settings)
        result = adapter.get("PROJ-2")

        assert result.ticket == "CUSTOM-123"
        assert result.feature == "FEATURE-123"
        assert result.team == "CustomTeam"
        assert result.region == "CustomRegion"
