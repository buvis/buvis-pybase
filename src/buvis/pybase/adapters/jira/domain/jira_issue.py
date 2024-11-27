from buvis.pybase.adapters.jira.exceptions.issue_update_failed import IssueUpdateFailed


class JiraIssue:

    def __init__(self, issue, server):
        self._issue = issue
        self._server = server

    @property
    def key(self):
        return self._issue.key

    @property
    def link(self):
        return f"[{self._issue.key}]({self._server}/browse/{self._issue.key})"

    @property
    def description(self):
        return self._issue.fields.description.strip().splitlines()

    @property
    def title(self):
        return str(self._issue.fields.summary.strip().splitlines()[0])

    @property
    def ticket(self):
        return str(self._issue.fields.customfield_11502)

    def update(self, **kwargs):
        try:
            self._issue.update(**kwargs)
        except Exception as e:
            raise IssueUpdateFailed(e) from e
