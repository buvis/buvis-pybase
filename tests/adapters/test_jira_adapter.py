from __future__ import annotations

import os
from unittest.mock import MagicMock, call, patch

import pytest
from jira.exceptions import JIRAError

from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO
from buvis.pybase.adapters.jira.domain.jira_search_result import JiraSearchResult
from buvis.pybase.adapters.jira.jira import JiraAdapter
from buvis.pybase.adapters.jira.settings import JiraFieldMappings, JiraSettings
from buvis.pybase.adapters.jira.exceptions import JiraNotFoundError


@pytest.fixture
def jira_settings(monkeypatch: pytest.MonkeyPatch) -> JiraSettings:
    """Create JiraSettings backed by the expected env vars."""
    monkeypatch.setenv("BUVIS_JIRA_SERVER", "https://jira.example.com")
    monkeypatch.setenv("BUVIS_JIRA_TOKEN", "test-token")
    monkeypatch.delenv("BUVIS_JIRA_PROXY", raising=False)
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
        """Valid settings create JIRA client."""
        JiraAdapter(jira_settings)

        mock_jira.assert_called_once_with(
            server="https://jira.example.com",
            token_auth="test-token",
        )

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_sets_proxy_when_configured(
        self, mock_jira: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Proxy config sets https_proxy env var and clears existing."""
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
        sample_issue_dto: JiraIssueDTO,
        jira_settings: JiraSettings,
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
        field_mappings = jira_settings.field_mappings
        assert field_mappings == JiraFieldMappings()
        assert call_fields["project"] == {"key": "PROJ"}
        assert call_fields["summary"] == "Test Issue"
        assert call_fields["assignee"] == {"key": "testuser", "name": "testuser"}
        assert call_fields[field_mappings.team] == {"value": "DevTeam"}
        assert call_fields[field_mappings.feature] == "EPIC-456"
        assert call_fields[field_mappings.ticket] == "PARENT-123"

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_returns_dto_with_id_and_link(
        self,
        mock_jira_cls: MagicMock,
        sample_issue_dto: JiraIssueDTO,
        jira_settings: JiraSettings,
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
        sample_issue_dto: JiraIssueDTO,
        jira_settings: JiraSettings,
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
        mappings = jira_settings.field_mappings
        mock_fetched_issue.update.assert_any_call(**{mappings.feature: "EPIC-456"})
        mock_fetched_issue.update.assert_any_call(**{mappings.region: {"value": "US"}})


class TestJiraAdapterGet:
    """Test JiraAdapter.get() method."""

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_returns_issue_dto(
        self, mock_jira_cls, jira_settings: JiraSettings
    ) -> None:
        """get() translates issue details into JiraIssueDTO."""
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
        mock_issue.fields.assignee.key = "testuser"
        mock_issue.fields.reporter.key = "reporter"
        mappings = jira_settings.field_mappings
        setattr(mock_issue.fields, mappings.ticket, "PARENT-123")
        setattr(mock_issue.fields, mappings.feature, "EPIC-456")
        team_field = MagicMock()
        team_field.value = "DevTeam"
        setattr(mock_issue.fields, mappings.team, team_field)
        region_field = MagicMock()
        region_field.value = "US"
        setattr(mock_issue.fields, mappings.region, region_field)
        mock_jira.issue.return_value = mock_issue

        adapter = JiraAdapter(jira_settings)
        result = adapter.get("PROJ-123")

        assert result.project == "PROJ"
        assert result.ticket == "PARENT-123"
        assert result.feature == "EPIC-456"
        assert result.team == "DevTeam"
        assert result.region == "US"
        assert result.id == "PROJ-123"
        assert result.link == "https://jira.example.com/browse/PROJ-123"
        mock_jira.issue.assert_called_once_with("PROJ-123")

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_raises_not_found(self, mock_jira_cls, jira_settings: JiraSettings) -> None:
        """get() raises JiraNotFoundError when JIRA returns 404."""
        mock_jira = mock_jira_cls.return_value
        error = JIRAError("Not found")
        error.status_code = 404
        mock_jira.issue.side_effect = error

        adapter = JiraAdapter(jira_settings)

        with pytest.raises(JiraNotFoundError) as excinfo:
            adapter.get("PROJ-404")

        assert excinfo.value.issue_key == "PROJ-404"

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_propagates_other_errors(
        self, mock_jira_cls, jira_settings: JiraSettings
    ) -> None:
        """get() re-raises JIRAError if status is not 404."""
        mock_jira = mock_jira_cls.return_value
        error = JIRAError("Server error")
        error.status_code = 500
        mock_jira.issue.side_effect = error

        adapter = JiraAdapter(jira_settings)

        with pytest.raises(JIRAError):
            adapter.get("PROJ-500")


class TestJiraAdapterUpdate:
    """Test JiraAdapter.update() method."""

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_calls_issue_update_with_fields(
        self, mock_jira_cls: MagicMock, jira_settings: JiraSettings
    ) -> None:
        """update() forwards the provided fields to issue.update()."""
        mock_jira = mock_jira_cls.return_value
        issue = MagicMock()
        mock_jira.issue.return_value = issue

        adapter = JiraAdapter(jira_settings)
        adapter._issue_to_dto = MagicMock()

        adapter.update("PROJ-123", {"summary": "Updated"})

        issue.update.assert_called_once_with(fields={"summary": "Updated"})

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_returns_refreshed_issue_dto(
        self,
        mock_jira_cls: MagicMock,
        jira_settings: JiraSettings,
        sample_issue_dto: JiraIssueDTO,
    ) -> None:
        """update() returns DTO generated from a refreshed issue."""
        mock_jira = mock_jira_cls.return_value
        original_issue = MagicMock()
        refreshed_issue = MagicMock()
        mock_jira.issue.side_effect = [original_issue, refreshed_issue]
        adapter = JiraAdapter(jira_settings)
        adapter._issue_to_dto = MagicMock(return_value=sample_issue_dto)

        result = adapter.update("PROJ-123", {"summary": "Updated"})

        assert result is sample_issue_dto
        adapter._issue_to_dto.assert_called_once_with(refreshed_issue)

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_raises_not_found_for_missing_issue(
        self, mock_jira_cls: MagicMock, jira_settings: JiraSettings
    ) -> None:
        """update() raises JiraNotFoundError when the issue cannot be found."""
        mock_jira = mock_jira_cls.return_value
        error = JIRAError("Not found")
        error.status_code = 404
        mock_jira.issue.side_effect = error

        adapter = JiraAdapter(jira_settings)

        with pytest.raises(JiraNotFoundError) as excinfo:
            adapter.update("PROJ-404", {"summary": "Updated"})

        assert excinfo.value.issue_key == "PROJ-404"


def _make_search_result(issues: list, total: int) -> MagicMock:
    """Return a mock JIRA search result with the requested issues."""
    mock_result = MagicMock()
    mock_result.total = total
    mock_result.__iter__.return_value = iter(issues)
    return mock_result


class TestJiraAdapterSearch:
    """Test JiraAdapter.search() method."""

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_search_returns_jira_search_result(
        self,
        mock_jira_cls: MagicMock,
        jira_settings: JiraSettings,
        sample_issue_dto: JiraIssueDTO,
    ) -> None:
        """search() returns JiraSearchResult with pagination data."""
        mock_jira = mock_jira_cls.return_value
        mock_issue = MagicMock()
        mock_jira.search_issues.return_value = _make_search_result(
            [mock_issue], total=3
        )
        adapter = JiraAdapter(jira_settings)
        adapter._issue_to_dto = MagicMock(return_value=sample_issue_dto)

        result = adapter.search("project = PROJ", start_at=2, max_results=25)

        assert isinstance(result, JiraSearchResult)
        assert result.issues == [sample_issue_dto]
        assert result.total == 3
        assert result.start_at == 2
        assert result.max_results == 25

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_search_passes_pagination_params(
        self,
        mock_jira_cls: MagicMock,
        jira_settings: JiraSettings,
        sample_issue_dto: JiraIssueDTO,
    ) -> None:
        """search() forwards start/max/fields to the JIRA client."""
        mock_jira = mock_jira_cls.return_value
        mock_jira.search_issues.return_value = _make_search_result([], total=0)
        adapter = JiraAdapter(jira_settings)
        adapter._issue_to_dto = MagicMock(return_value=sample_issue_dto)

        adapter.search(
            "project = PROJ", start_at=5, max_results=10, fields=["id", "summary"]
        )

        mock_jira.search_issues.assert_called_once_with(
            "project = PROJ", startAt=5, maxResults=10, fields=["id", "summary"]
        )

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_search_converts_issues_to_dto(
        self, mock_jira_cls: MagicMock, jira_settings: JiraSettings
    ) -> None:
        """search() converts each issue to a DTO via _issue_to_dto."""
        mock_jira = mock_jira_cls.return_value
        issue_one = MagicMock()
        issue_two = MagicMock()
        mock_jira.search_issues.return_value = _make_search_result(
            [issue_one, issue_two], total=2
        )
        adapter = JiraAdapter(jira_settings)
        adapter._issue_to_dto = MagicMock(
            return_value=JiraIssueDTO(
                project="PROJ",
                title="Sample",
                description="desc",
                issue_type="Task",
                labels=[],
                priority="Low",
                ticket="PARENT-1",
                feature="EPIC-1",
                assignee="user",
                reporter="user",
                team="Team",
                region="Region",
            )
        )

        adapter.search("project = PROJ")

        adapter._issue_to_dto.assert_has_calls([call(issue_one), call(issue_two)])

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_search_has_more_property(
        self,
        mock_jira_cls: MagicMock,
        jira_settings: JiraSettings,
        sample_issue_dto: JiraIssueDTO,
    ) -> None:
        """JiraSearchResult.has_more reflects total vs returned count."""
        mock_jira = mock_jira_cls.return_value
        mock_issue = MagicMock()
        mock_jira.search_issues.return_value = _make_search_result(
            [mock_issue], total=5
        )
        adapter = JiraAdapter(jira_settings)
        adapter._issue_to_dto = MagicMock(return_value=sample_issue_dto)

        result = adapter.search("project = PROJ")

        assert result.has_more

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_search_handles_empty_results(
        self, mock_jira_cls: MagicMock, jira_settings: JiraSettings
    ) -> None:
        """search() handles empty results without issues."""
        mock_jira = mock_jira_cls.return_value
        mock_jira.search_issues.return_value = _make_search_result([], total=0)
        adapter = JiraAdapter(jira_settings)
        adapter._issue_to_dto = MagicMock()

        result = adapter.search("project = PROJ")

        assert result.issues == []
        assert result.total == 0
        assert result.start_at == 0
        assert result.max_results == 50
        assert not result.has_more
