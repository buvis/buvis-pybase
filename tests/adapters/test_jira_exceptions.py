from __future__ import annotations

import pytest

from buvis.pybase.adapters.jira import (
    JiraError,
    JiraLinkError,
    JiraNotFoundError,
    JiraTransitionError,
)


def test_jira_error_can_be_raised_and_caught() -> None:
    message = "custom failure"

    with pytest.raises(JiraError, match=message):
        raise JiraError(message)


def test_jira_not_found_error_inherits_and_exposes_context() -> None:
    issue_key = "PROJ-1"

    with pytest.raises(JiraNotFoundError, match=issue_key) as exc_info:
        raise JiraNotFoundError(issue_key)

    error = exc_info.value
    assert isinstance(error, JiraError)
    assert error.issue_key == issue_key


def test_jira_transition_error_message_and_attributes() -> None:
    issue_key = "PROJ-2"
    transition = "Done"

    with pytest.raises(JiraTransitionError, match=transition) as exc_info:
        raise JiraTransitionError(issue_key, transition)

    error = exc_info.value
    assert issue_key in str(error)
    assert error.issue_key == issue_key
    assert error.transition == transition


def test_jira_link_error_message_and_context() -> None:
    from_key = "PROJ-3"
    to_key = "PROJ-4"
    link_type = "Blocks"

    with pytest.raises(JiraLinkError, match=link_type) as exc_info:
        raise JiraLinkError(from_key, to_key, link_type)

    error = exc_info.value
    assert from_key in str(error)
    assert to_key in str(error)
    assert error.from_key == from_key
    assert error.to_key == to_key
    assert error.link_type == link_type
