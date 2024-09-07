from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Capture
    from rich.status import Status

from rich.console import Console
from rich.prompt import Confirm

CHECKMARK = "[bold green1]\u2714[/bold green1]"
WARNING = "[bold orange3]\u26a0[/bold orange3]"
CROSSMARK = "[bold indian_red]\u2718[/bold indian_red]"
STYLE_SUCCESS_MSG = "spring_green1"
STYLE_WARNING_MSG = "light_goldenrod3"
STYLE_FAILURE_MSG = "bold light_salmon3"


class ConsoleAdapter:
    def __init__(self: ConsoleAdapter) -> None:
        self.console = Console(log_path=False)

    def format_success(self: ConsoleAdapter, message: str) -> str:
        return f" {CHECKMARK} [{STYLE_SUCCESS_MSG}]{message}[/{STYLE_SUCCESS_MSG}]"

    def success(self: ConsoleAdapter, message: str) -> None:
        self.console.print(self.format_success(message))

    def format_warning(self: ConsoleAdapter, message: str) -> str:
        return f" {WARNING} [{STYLE_WARNING_MSG}]{message}[/{STYLE_WARNING_MSG}]"

    def warning(self: ConsoleAdapter, message: str) -> None:
        self.console.print(self.format_warning(message))

    def format_failure(self: ConsoleAdapter, message: str, details: str = "") -> str:
        formatted_message = (
            f" {CROSSMARK} [{STYLE_FAILURE_MSG}]{message}[/{STYLE_FAILURE_MSG}]"
        )
        if details:
            formatted_message += " \n\n Details:\n\n {details}"

        return formatted_message

    def failure(self: ConsoleAdapter, message: str, details: str = "") -> None:
        self.console.print(self.format_failure(message, details))

    def panic(self: ConsoleAdapter, message: str, details: str = "") -> None:
        self.failure(message, details)
        sys.exit()

    def status(self: ConsoleAdapter, message: str) -> Status:
        return self.console.status(message, spinner="arrow3")

    def capture(self: ConsoleAdapter) -> Capture:
        return self.console.capture()

    def confirm(self: ConsoleAdapter, message: str) -> bool:
        return Confirm.ask(message)

    def print(self: ConsoleAdapter, message: str) -> None:
        return self.console.print(message)

    def nl(self: ConsoleAdapter) -> None:
        return self.console.out("")


console = ConsoleAdapter()
