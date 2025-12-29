from dataclasses import dataclass


@dataclass
class JiraIssueDTO:
    project: str
    title: str
    description: str
    issue_type: str
    labels: list
    priority: str
    ticket: str
    feature: str
    assignee: str
    reporter: str
    team: str
    region: str
    id: str | None = None
    link: str | None = None
