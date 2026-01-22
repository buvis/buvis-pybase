"""JIRA REST API adapter for issue creation.

Provides JiraAdapter for creating JIRA issues with custom field support.
"""

import os

from jira import JIRA

from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO
from buvis.pybase.adapters.jira.settings import JiraSettings


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

        return JiraIssueDTO(
            project=new_issue.fields.project.key,
            title=new_issue.fields.summary,
            description=new_issue.fields.description,
            issue_type=new_issue.fields.issuetype.name,
            labels=new_issue.fields.labels,
            priority=new_issue.fields.priority.name,
            ticket=getattr(new_issue.fields, mappings.ticket, None),
            feature=getattr(new_issue.fields, mappings.feature, None),
            assignee=new_issue.fields.assignee.key,
            reporter=new_issue.fields.reporter.key,
            team=getattr(getattr(new_issue.fields, mappings.team, None), "value", None),
            region=getattr(
                getattr(new_issue.fields, mappings.region, None), "value", None
            ),
            id=new_issue.key,
            link=new_issue.permalink(),
        )
