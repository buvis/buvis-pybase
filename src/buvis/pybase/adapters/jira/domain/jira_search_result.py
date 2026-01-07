from __future__ import annotations
from dataclasses import dataclass

from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO

__all__ = ["JiraSearchResult"]


@dataclass
class JiraSearchResult:
    """Paginated JIRA search results."""

    issues: list[JiraIssueDTO]
    total: int
    start_at: int
    max_results: int
