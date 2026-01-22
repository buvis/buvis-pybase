from __future__ import annotations

__all__ = [
    "JiraError",
    "JiraLinkError",
    "JiraNotFoundError",
    "JiraTransitionError",
]


class JiraError(Exception):
    """Base exception for JIRA operations."""

    def __init__(self, message: str = "JIRA operation failed.") -> None:
        super().__init__(message)


class JiraNotFoundError(JiraError):
    """Issue not found in JIRA."""

    def __init__(self, issue_key: str) -> None:
        super().__init__(f"Issue not found: {issue_key}")
        self.issue_key = issue_key


class JiraTransitionError(JiraError):
    """Transition unavailable or failed."""

    def __init__(self, issue_key: str, transition: str) -> None:
        super().__init__(f"Transition '{transition}' unavailable for {issue_key}")
        self.issue_key = issue_key
        self.transition = transition


class JiraLinkError(JiraError):
    """Issue link creation failed."""

    def __init__(self, from_key: str, to_key: str, link_type: str) -> None:
        super().__init__(f"Failed to link {from_key} -> {to_key} ({link_type})")
        self.from_key = from_key
        self.to_key = to_key
        self.link_type = link_type
