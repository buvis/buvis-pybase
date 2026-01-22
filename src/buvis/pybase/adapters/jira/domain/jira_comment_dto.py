from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

__all__ = ["JiraCommentDTO"]


@dataclass
class JiraCommentDTO:
    """DTO for JIRA issue comments.

    Attributes:
        body: Comment text content.
        author: Username of comment author.
        created: Timestamp when comment was created.
        is_internal: True if comment is internal (Service Desk visibility).
        id: Server-assigned comment ID.
    """

    body: str
    author: str | None = None
    created: datetime | None = None
    is_internal: bool = False
    id: str | None = None
