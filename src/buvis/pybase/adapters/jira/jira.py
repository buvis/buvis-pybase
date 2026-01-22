"""JIRA REST API adapter for issue creation.

Provides JiraAdapter for creating JIRA issues with custom field support.
"""

import os

from jira import JIRA
from jira.exceptions import JIRAError

from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO
from buvis.pybase.adapters.jira.domain.jira_search_result import JiraSearchResult
from buvis.pybase.adapters.jira.settings import JiraSettings
from buvis.pybase.adapters.jira.exceptions import JiraNotFoundError


class JiraAdapter:
    """JIRA REST API adapter for issue creation.

    Requirements:
        JiraSettings must provide `server` and `token`.

    Optional:
        Set `proxy` in the settings to route requests through a proxy server.

    Example:
        >>> settings = JiraSettings()  # provides server, token
        >>> jira = JiraAdapter(settings)
        >>> issue = JiraIssueDTO(project='PROJ', title='Bug', ...)
        >>> created = jira.create(issue)
        >>> print(created.link)
    """

    def __init__(self, settings: JiraSettings) -> None:
        """Initialize JIRA connection.

        Args:
            settings: JiraSettings with server, token, optional proxy.
        """
        self._settings = settings
        self._fields = settings.field_mappings
        if settings.proxy:
            os.environ.pop("https_proxy", None)
            os.environ.pop("http_proxy", None)
            os.environ["https_proxy"] = settings.proxy

        self._jira = JIRA(
            server=settings.server,
            token_auth=settings.token,
        )

    def create(self, issue: JiraIssueDTO) -> JiraIssueDTO:
        """Create a JIRA issue via the REST API.

        Args:
            issue (JiraIssueDTO): containing all required fields.

        Returns:
            JiraIssueDTO: populated with server-assigned id and link.

        Custom Field Mappings:
            ticket -> configured JiraFieldMappings ticket value
            team -> configured JiraFieldMappings team value
            feature -> configured JiraFieldMappings feature value
            region -> configured JiraFieldMappings region value

        Note:
            Custom fields feature and region require post-creation update due to JIRA API limitations.
        """
        mappings = self._fields
        new_issue = self._jira.create_issue(
            fields={
                "assignee": {"key": issue.assignee, "name": issue.assignee},
                mappings.feature: issue.feature,
                mappings.team: {"value": issue.team},
                mappings.region: {"value": issue.region},
                mappings.ticket: issue.ticket,
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
        new_issue.update(**{mappings.feature: issue.feature})
        new_issue.update(**{mappings.region: {"value": issue.region}})

        return self._issue_to_dto(new_issue)

    def _issue_to_dto(self, issue) -> JiraIssueDTO:
        """Convert a JIRA issue response into a DTO."""
        fields = issue.fields
        mappings = self._fields

        def _custom_field(field_name: str, attr: str | None = None):
            value = getattr(fields, field_name, None)
            if value is None:
                return None
            return getattr(value, attr, None) if attr else value

        return JiraIssueDTO(
            project=fields.project.key,
            title=fields.summary,
            description=fields.description,
            issue_type=fields.issuetype.name,
            labels=fields.labels,
            priority=fields.priority.name,
            ticket=_custom_field(mappings.ticket),
            feature=_custom_field(mappings.feature),
            assignee=fields.assignee.key,
            reporter=fields.reporter.key,
            team=_custom_field(mappings.team, "value"),
            region=_custom_field(mappings.region, "value"),
            id=issue.key,
            link=issue.permalink(),
        )

    def search(
        self,
        jql: str,
        start_at: int = 0,
        max_results: int = 50,
        fields: list[str] | None = None,
    ) -> JiraSearchResult:
        """Search issues using JQL.

        Args:
            jql: JQL query string.
            start_at: Pagination offset (0-based).
            max_results: Max issues to return (default 50).
            fields: Specific fields to retrieve (None = all).

        Returns:
            JiraSearchResult with matching issues and pagination info.
        """
        result = self._jira.search_issues(
            jql,
            startAt=start_at,
            maxResults=max_results,
            fields=fields,
        )

        return JiraSearchResult(
            issues=[self._issue_to_dto(issue) for issue in result],
            total=result.total,
            start_at=start_at,
            max_results=max_results,
        )

    def get(self, issue_key: str) -> JiraIssueDTO:
        """Fetch issue by key.

        Args:
            issue_key: JIRA issue key (e.g., 'PROJ-123').

        Returns:
            JiraIssueDTO with issue data.

        Raises:
            JiraNotFoundError: Issue does not exist.
        """
        try:
            issue = self._jira.issue(issue_key)
        except JIRAError as e:
            if getattr(e, "status_code", None) == 404:
                raise JiraNotFoundError(issue_key) from e
            raise

        return self._issue_to_dto(issue)

    def update(self, issue_key: str, fields: dict) -> JiraIssueDTO:
        """Update issue fields.

        Args:
            issue_key: Issue to update.
            fields: Dict of field names/IDs to new values.

        Returns:
            JiraIssueDTO with updated issue data.

        Raises:
            JiraNotFoundError: Issue does not exist.
        """
        try:
            issue = self._jira.issue(issue_key)
        except JIRAError as e:
            if e.status_code == 404:
                raise JiraNotFoundError(issue_key) from e
            raise

        issue.update(fields=fields)

        # Refresh to get updated values
        updated = self._jira.issue(issue_key)
        return self._issue_to_dto(updated)
