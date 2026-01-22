from __future__ import annotations

from dataclasses import dataclass

from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO

__all__ = ["JiraSearchResult"]


@dataclass
class JiraSearchResult:
    """Paginated search result from JQL query.

    Attributes:
        issues: List of matching issues.
        total: Total matches (may exceed len(issues)).
        start_at: Offset of first returned issue.
        max_results: Maximum issues requested.
    """

    issues: list[JiraIssueDTO]
    total: int
    start_at: int
    max_results: int

    @property
    def has_more(self) -> bool:
        """True if more results available beyond current page."""
        return self.start_at + len(self.issues) < self.total
