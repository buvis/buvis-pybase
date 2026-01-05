from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO
from buvis.pybase.adapters.jira.jira import JiraAdapter  # noqa: F401


@pytest.fixture
def mock_config() -> MagicMock:
    """Create a mock config object with default valid values."""
    config = MagicMock()
    config.get_configuration_item_or_default.side_effect = lambda key, default: {
        "server": "https://jira.example.com",
        "token": "test-token",
        "proxy": None,
    }.get(key, default)
    config.get_configuration_item.side_effect = lambda key: {
        "server": "https://jira.example.com",
        "token": "test-token",
    }[key]
    return config


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


@pytest.fixture
def mock_jira_client():
    """Create a mock JIRA client for testing."""
    with patch("buvis.pybase.adapters.jira.jira.JIRA") as mock_jira_class:
        mock_client = MagicMock()
        mock_jira_class.return_value = mock_client
        yield mock_client


class TestJiraAdapterInit:
    """Test JiraAdapter initialization."""

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_raises_when_server_missing(self, mock_jira: MagicMock) -> None:
        """Missing server raises ValueError."""
        config = MagicMock()
        config.get_configuration_item_or_default.side_effect = lambda key, default: {
            "server": None,
            "token": "test-token",
            "proxy": None,
        }.get(key, default)

        with pytest.raises(ValueError, match="Server and token must be provided"):
            JiraAdapter(config)

        mock_jira.assert_not_called()


class TestJiraAdapterCreate:
    """Test JiraAdapter.create() method."""

    pass
