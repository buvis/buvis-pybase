import os

if os.name == "nt":
    from .outlook_local.outlook_local import OutlookLocalAdapter

from .console.console import console, logging_to_console
from .poetry.poetry import PoetryAdapter
from .shell.shell import ShellAdapter

__all__ = ["console", "PoetryAdapter", "ShellAdapter", "logging_to_console"]
