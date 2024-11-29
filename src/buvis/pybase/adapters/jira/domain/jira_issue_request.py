from dataclasses import dataclass

from jira_syncer.app.config import cfg

@dataclass
class JiraIssueRequest:
    title: str
    description: str
    feature: str
    labels: list
    priority: dict
    ticket: str

    # def __init__(self, loop):
    #     self._loop = loop
    #
    # @property
    # def id(self):
    #     return self._loop.id
    #
    # @property
    # def title(self):
    #     if "#pex" in self._loop.tags:
    #         return f"PEX: {self._loop.title}"
    #     else:
    #         return str(self._loop.title)
    #
    # @property
    # def ticket(self):
    #     return str(self._loop.ticket)
    #
    # @property
    # def user_story(self):
    #     return self._loop.user_story
    #
    # @property
    # def description(self):
    #     if description := "\n".join(
    #             self._loop.description.strip().splitlines()):
    #         ticket_references = self._get_ticket_references()
    #
    #         if ticket_references != "":
    #             description += f"\n\n{ticket_references}"
    #
    #         return description.splitlines()
    #
    # @property
    # def deliverable(self):
    #     return str(self._loop.deliverable)
    #
    # def is_excluded_from_tracking(self):
    #     if self.user_story is not None:
    #         if isinstance(self.user_story, set):
    #             for us in self.user_story:
    #                 if us.key == cfg.us_ignore:
    #                     return True
    #         elif self.user_story.key == cfg.us_ignore:
    #             return True
    #
    #     return False
    #
    # def _get_ticket_references(self):
    #     ref_text = ""
    #
    #     if hasattr(self._loop, "ticket") and self._loop.ticket is not None:
    #         ref_text = f"This solves SR {self._loop.ticket}."
    #
    #     if (hasattr(self._loop, "ticket_related")
    #             and self._loop.ticket_related is not None):
    #         if isinstance(self._loop.ticket_related, set):
    #             ticket_list = sorted(self._loop.ticket_related)
    #
    #             if len(ticket_list) > 1:
    #                 ticket_list_str = (", ".join(ticket_list[:-1]) + ", and " +
    #                                    ticket_list[-1])
    #                 ref_text += f" Related SRs: {ticket_list_str}."
    #         else:
    #             ref_text += f" Related SR: {self._loop.ticket_related}."
    #
    #     return ref_text
