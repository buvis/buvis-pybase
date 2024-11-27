import os

if os.name == "nt":
    from .outlook_local.outlook_local import OutlookLocalAdapter

from .console.console import console, logging_to_console
from .poetry.poetry import PoetryAdapter
from .shell.shell import ShellAdapter
from .jira.jira import JiraAdapter

__all__ = ["console", "JiraAdapter", "PoetryAdapter", "ShellAdapter", "logging_to_console"]
