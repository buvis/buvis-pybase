import os
from jira import JIRA
from buvis.pybase.adapters.jira.domain.jira_issue import JiraIssue
from buvis.pybase.configuration import Configuration


class JiraAdapter:

    def __init__(self: "JiraAdapter", cfg: Configuration) -> None:
        self._cfg = cfg
        if self._cfg["proxy"]:
            os.environ.pop("https_proxy")
            os.environ.pop("http_proxy")
            os.environ["https_proxy"] = self._cfg["proxy"]
        self._jira = JIRA(server=self._cfg["server"], token_auth=self._cfg["token"])
        self._default_project = {"key": self._cfg["defaults"]["project"]}
        self._default_team = {"value": self._cfg["defaults"]["team"]}
        self._default_region = {"value": self._cfg["defaults"]["region"]}
        self._default_user = {"key": self._cfg["defaults"]["user"], "name": self._cfg["defaults"]["user"]}

    def create_issue(self,
                     title: str,
                     description: str,
                     feature: str,
                     issue_type: dict,
                     labels: list,
                     priority: dict,
                     ticket: str):
        new_issue = self._jira.create_issue(
            fields={
                "assignee": self._default_user,
                "customfield_10001": feature,
                "customfield_10501": self._default_team,
                "customfield_12900": self._default_region,
                "customfield_11502": ticket,
                "description": description,
                "issuetype": issue_type,
                "labels": labels,
                "priority": priority,
                "project": self._default_project,
                "reporter": self._default_user,
                "summary": title,
            })
        # some custom fields aren't populated on issue creation
        # so I have to update them after issue creation
        new_issue = self._jira.issue(new_issue.key)
        new_issue.update(customfield_10001=feature)
        new_issue.update(customfield_12900=self._default_region)

        return JiraIssue(new_issue, self._cfg["server"])
