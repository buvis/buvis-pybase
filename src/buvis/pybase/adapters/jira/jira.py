"""JIRA REST API adapter for issue creation.

Provides JiraAdapter for creating JIRA issues with custom field support.
"""

import logging
import os
from typing import Any

from jira import JIRA
from jira.exceptions import JIRAError

from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO
from buvis.pybase.adapters.jira.domain import JiraSearchResult
from buvis.pybase.adapters.jira.exceptions import JiraNotFoundError
from buvis.pybase.adapters.jira.settings import JiraSettings


class JiraAdapter:
    """JIRA REST API adapter for issue creation.

    Requirements:
        Provide a populated `JiraSettings` instance with `server` and `token`.

    Optional:
        Configure `proxy` in the settings to route requests through a proxy server.

    Example:
        >>> settings = JiraSettings(server="https://jira", token="abc123")
        >>> jira = JiraAdapter(settings)
        >>> issue = JiraIssueDTO(...)
        >>> created = jira.create(issue)
        >>> print(created.link)
    """

    def __init__(self: "JiraAdapter", settings: JiraSettings) -> None:
        """Initialize JIRA connection.

        Args:
            settings: JiraSettings instance with server/token values.
        """
        self.logger = logging.getLogger(__name__)
        self._settings = settings
        if self._settings.proxy:
            os.environ.pop("https_proxy", None)
            os.environ.pop("http_proxy", None)
            os.environ["https_proxy"] = str(self._settings.proxy)

        self._jira = JIRA(
            server=str(self._settings.server),
            token_auth=str(self._settings.token),
        )

    def create(self, issue: JiraIssueDTO) -> JiraIssueDTO:
        """Create a JIRA issue via the REST API.

        Args:
            issue (JiraIssueDTO): containing all required fields.

        Returns:
            JiraIssueDTO: populated with server-assigned id and link.

        Custom Field Mappings:
            Determined by `self._settings.field_mappings`. Defaults:
            ticket -> customfield_11502, team -> customfield_10501,
            feature -> customfield_10001, region -> customfield_12900.

        Note:
            Custom fields customfield_10001 (feature) and customfield_12900 (region) require post-creation update due to JIRA API limitations.
        """
        field_mappings = self._settings.field_mappings

        new_issue = self._jira.create_issue(
            fields={
                "assignee": {"key": issue.assignee, "name": issue.assignee},
                field_mappings.feature: issue.feature,
                field_mappings.team: {"value": issue.team},
                field_mappings.region: {"value": issue.region},
                field_mappings.ticket: issue.ticket,
                "description": issue.description,
                "issuetype": {"name": issue.issue_type},
                "labels": issue.labels,
                "priority": {"name": issue.priority},
                "project": {"key": issue.project},
                "reporter": {"key": issue.reporter, "name": issue.reporter},
                "summary": issue.title,
            },
        )
        # some custom fields aren't populated on issue creation
        # so I have to update them after issue creation
        new_issue = self._jira.issue(new_issue.key)
        new_issue.update(**{field_mappings.feature: issue.feature})
        new_issue.update(**{field_mappings.region: {"value": issue.region}})

        ticket_value = getattr(new_issue.fields, field_mappings.ticket, None)
        feature_value = getattr(new_issue.fields, field_mappings.feature, None)
        team_field_value = getattr(new_issue.fields, field_mappings.team, None)
        region_field_value = getattr(new_issue.fields, field_mappings.region, None)

        return JiraIssueDTO(
            project=new_issue.fields.project.key,
            title=new_issue.fields.summary,
            description=new_issue.fields.description,
            issue_type=new_issue.fields.issuetype.name,
            labels=new_issue.fields.labels,
            priority=new_issue.fields.priority.name,
            ticket=ticket_value,
            feature=feature_value,
            assignee=new_issue.fields.assignee.key,
            reporter=new_issue.fields.reporter.key,
            team=getattr(team_field_value, "value", None),
            region=getattr(region_field_value, "value", None),
            id=new_issue.key,
            link=new_issue.permalink(),
        )

    def _issue_to_dto(self, issue) -> JiraIssueDTO:
        """Convert JIRA issue object to DTO."""
        fm = self._settings.field_mappings
        team_val = getattr(issue.fields, fm.team, None)
        region_val = getattr(issue.fields, fm.region, None)
        return JiraIssueDTO(
            project=issue.fields.project.key,
            title=issue.fields.summary,
            description=issue.fields.description or "",
            issue_type=issue.fields.issuetype.name,
            labels=issue.fields.labels or [],
            priority=issue.fields.priority.name if issue.fields.priority else "Medium",
            ticket=getattr(issue.fields, fm.ticket, "") or "",
            feature=getattr(issue.fields, fm.feature, "") or "",
            assignee=issue.fields.assignee.key if issue.fields.assignee else "",
            reporter=issue.fields.reporter.key if issue.fields.reporter else "",
            team=getattr(team_val, "value", None) if team_val else None,
            region=getattr(region_val, "value", None) if region_val else None,
            id=issue.key,
            link=issue.permalink(),
        )

    def get(self, issue_key: str) -> JiraIssueDTO:
        """Retrieve issue by key.

        Raises:
            JiraNotFoundError: Issue does not exist.
        """
        try:
            issue = self._jira.issue(issue_key)
        except JIRAError as error:
            if getattr(error, "status_code", None) == 404:
                raise JiraNotFoundError(issue_key) from error
            raise

        return self._issue_to_dto(issue)

    def search(
        self,
        jql: str,
        start_at: int = 0,
        max_results: int = 50,
        fields: str | None = None,
    ) -> JiraSearchResult:
        """Execute JQL query with pagination."""
        results = self._jira.search_issues(
            jql,
            startAt=start_at,
            maxResults=max_results,
            fields=fields,
        )
        issues = [self._issue_to_dto(issue) for issue in results]
        return JiraSearchResult(
            issues=issues,
            total=results.total,
            start_at=start_at,
            max_results=max_results,
        )

    def update(self, issue_key: str, fields: dict[str, Any]) -> JiraIssueDTO:
        """Update issue fields.

        Args:
            issue_key: Issue to update.
            fields: Dict of field names to new values.

        Returns:
            Updated JiraIssueDTO.

        Raises:
            JiraNotFoundError: Issue does not exist.
        """
        # Verify issue exists (raises JiraNotFoundError if not)
        self.get(issue_key)

        issue = self._jira.issue(issue_key)
        issue.update(fields=fields)

        return self.get(issue_key)
