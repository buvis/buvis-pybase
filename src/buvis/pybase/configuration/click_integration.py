"""Click integration for BUVIS configuration."""

from __future__ import annotations

import functools
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, TypeVar

import click

from .resolver import ConfigResolver
from .settings import GlobalSettings

if TYPE_CHECKING:
    from collections.abc import Callable


def get_settings(ctx: click.Context) -> GlobalSettings:
    """Get settings from Click context.

    Args:
        ctx: Click context with settings stored by buvis_options decorator.

    Raises:
        RuntimeError: If called before buvis_options decorator ran.

    Returns:
        The GlobalSettings instance from context.
    """
    if ctx.obj is None or "settings" not in ctx.obj:
        msg = "get_settings() called but buvis_options decorator not applied"
        raise RuntimeError(msg)
    return ctx.obj["settings"]


F = TypeVar("F", bound=Callable[..., Any])


def buvis_options(f: F) -> F:
    """Add standard BUVIS options to a Click command.

    Adds ``--debug/--no-debug``, ``--log-level``, ``--config-dir``, and
    ``--config`` options. Resolves settings using ConfigResolver and
    injects into Click context.

    Example::

        @click.command()
        @buvis_options
        @click.pass_context
        def cli(ctx):
            settings = ctx.obj["settings"]
            if settings.debug:
                click.echo("Debug mode enabled")
    """

    @click.option(
        "--config",
        type=click.Path(exists=True, dir_okay=False, resolve_path=True),
        help="YAML config file path.",
    )
    @click.option(
        "--config-dir",
        type=click.Path(exists=True, file_okay=False, resolve_path=True),
        help="Configuration directory.",
    )
    @click.option(
        "--log-level",
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
        default=None,
        help="Logging level.",
    )
    @click.option(
        "--debug/--no-debug",
        default=None,
        help="Enable debug mode.",
    )
    @click.pass_context
    @functools.wraps(f)
    def wrapper(
        ctx: click.Context,
        debug: bool | None,
        log_level: str | None,
        config_dir: str | None,
        config: str | None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        cli_overrides = {
            k: v
            for k, v in {"debug": debug, "log_level": log_level}.items()
            if v is not None
        }

        resolver = ConfigResolver()
        settings = resolver.resolve(
            GlobalSettings,
            config_dir=config_dir,
            config_path=Path(config) if config else None,
            cli_overrides=cli_overrides,
        )

        ctx.ensure_object(dict)
        ctx.obj["settings"] = settings

        return ctx.invoke(f, *args, **kwargs)

    return wrapper  # type: ignore[return-value]
