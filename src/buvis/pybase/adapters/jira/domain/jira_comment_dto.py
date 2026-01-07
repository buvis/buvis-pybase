"""Data transfer objects used when interacting with JIRA."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

__all__ = ["JiraCommentDTO"]


@dataclass
class JiraCommentDTO:
    """DTO for JIRA issue comments."""

    id: str
    author: str
    body: str
    created: datetime
    is_internal: bool = False
