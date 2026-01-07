"""JIRA REST API adapter for issue creation.

Provides JiraAdapter for creating JIRA issues with custom field support.
"""

import logging
import os

from jira import JIRA

from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO
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
