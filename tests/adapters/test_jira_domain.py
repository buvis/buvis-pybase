from __future__ import annotations

from buvis.pybase.adapters.jira.domain.jira_comment_dto import JiraCommentDTO
from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO
from buvis.pybase.adapters.jira.domain.jira_search_result import JiraSearchResult


def build_issue(key: str) -> JiraIssueDTO:
    """Return a JiraIssueDTO with the required fields populated."""
    return JiraIssueDTO(
        project="PROJ",
        title="Sample Issue",
        description="Sample description",
        issue_type="Task",
        labels=["sample"],
        priority="Medium",
        ticket="PARENT-1",
        feature="EPIC-1",
        assignee="assignee",
        reporter="reporter",
        team="Dev",
        region="US",
        id=key,
        link=f"https://jira.example.com/browse/{key}",
    )


def test_jira_comment_dto_instantiation_defaults() -> None:
    """Required fields set while optional fields use their defaults."""
    comment = JiraCommentDTO(body="Example note")

    assert comment.body == "Example note"
    assert comment.author is None
    assert comment.created is None
    assert comment.is_internal is False
    assert comment.id is None


def test_jira_search_result_has_more_true() -> None:
    """has_more is True when more issues exist beyond the current page."""
    result = JiraSearchResult(
        issues=[build_issue("PROJ-1")],
        total=5,
        start_at=0,
        max_results=50,
    )

    assert result.has_more


def test_jira_search_result_has_more_false() -> None:
    """has_more is False when the current page covers all matches."""
    result = JiraSearchResult(
        issues=[build_issue("PROJ-1")],
        total=1,
        start_at=0,
        max_results=50,
    )

    assert not result.has_more
