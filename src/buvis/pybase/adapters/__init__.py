import os

if os.name == "nt":
    from .outlook_local.outlook_local import OutlookLocalAdapter

from .console.console import console, logging_to_console
from .poetry.poetry import PoetryAdapter

__all__ = ["console", "PoetryAdapter", "logging_to_console"]
