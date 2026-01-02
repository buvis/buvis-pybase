"""Tests for Click integration with BUVIS configuration."""

from __future__ import annotations

from pathlib import Path

import click
import pytest
from click.testing import CliRunner

from buvis.pybase.configuration import buvis_options, get_settings
from buvis.pybase.configuration.buvis_settings import BuvisSettings


@pytest.fixture
def runner() -> CliRunner:
    """Create Click test runner."""
    return CliRunner()


class TestBuvisOptionsHelp:
    """Tests for --help output."""

    def test_debug_option_in_help(self, runner: CliRunner) -> None:
        """--debug/--no-debug appears in help."""

        @click.command()
        @buvis_options
        def cmd() -> None:
            pass

        result = runner.invoke(cmd, ["--help"])

        assert "--debug" in result.output
        assert "--no-debug" in result.output

    def test_log_level_option_in_help(self, runner: CliRunner) -> None:
        """--log-level appears in help with choices."""

        @click.command()
        @buvis_options
        def cmd() -> None:
            pass

        result = runner.invoke(cmd, ["--help"])

        assert "--log-level" in result.output
        assert "debug" in result.output.lower()

    def test_config_dir_option_in_help(self, runner: CliRunner) -> None:
        """--config-dir appears in help."""

        @click.command()
        @buvis_options
        def cmd() -> None:
            pass

        result = runner.invoke(cmd, ["--help"])

        assert "--config-dir" in result.output

    def test_config_option_in_help(self, runner: CliRunner) -> None:
        """--config appears in help."""

        @click.command()
        @buvis_options
        def cmd() -> None:
            pass

        result = runner.invoke(cmd, ["--help"])

        assert "--config" in result.output


class TestBuvisOptionsContextInjection:
    """Tests for settings injection into context."""

    def test_settings_injected_into_context(self, runner: CliRunner) -> None:
        """Settings object exists in ctx.obj['settings']."""
        captured_settings = []

        @click.command()
        @buvis_options
        @click.pass_context
        def cmd(ctx: click.Context) -> None:
            captured_settings.append(ctx.obj.get("settings"))

        runner.invoke(cmd, [])

        assert len(captured_settings) == 1
        assert isinstance(captured_settings[0], BuvisSettings)

    def test_default_settings_values(self, runner: CliRunner) -> None:
        """Default settings have expected values."""
        captured_settings = []

        @click.command()
        @buvis_options
        @click.pass_context
        def cmd(ctx: click.Context) -> None:
            captured_settings.append(ctx.obj["settings"])

        runner.invoke(cmd, [])

        settings = captured_settings[0]
        assert settings.debug is False
        assert settings.log_level == "INFO"


class TestBuvisOptionsCLIOverrides:
    """Tests for CLI option overrides."""

    def test_debug_flag_overrides_default(self, runner: CliRunner) -> None:
        """--debug sets debug=True."""
        captured_settings = []

        @click.command()
        @buvis_options
        @click.pass_context
        def cmd(ctx: click.Context) -> None:
            captured_settings.append(ctx.obj["settings"])

        runner.invoke(cmd, ["--debug"])

        assert captured_settings[0].debug is True

    def test_no_debug_flag(self, runner: CliRunner) -> None:
        """--no-debug sets debug=False."""
        captured_settings = []

        @click.command()
        @buvis_options
        @click.pass_context
        def cmd(ctx: click.Context) -> None:
            captured_settings.append(ctx.obj["settings"])

        runner.invoke(cmd, ["--no-debug"])

        assert captured_settings[0].debug is False

    def test_log_level_override(self, runner: CliRunner) -> None:
        """--log-level sets log_level."""
        captured_settings = []

        @click.command()
        @buvis_options
        @click.pass_context
        def cmd(ctx: click.Context) -> None:
            captured_settings.append(ctx.obj["settings"])

        runner.invoke(cmd, ["--log-level", "DEBUG"])

        assert captured_settings[0].log_level == "DEBUG"


class TestBuvisOptionsConfigFile:
    """Tests for config file loading."""

    def test_config_file_loaded(self, runner: CliRunner, tmp_path: Path) -> None:
        """--config loads YAML file."""
        config = tmp_path / "config.yaml"
        config.write_text("debug: true\n")
        captured_settings = []

        @click.command()
        @buvis_options
        @click.pass_context
        def cmd(ctx: click.Context) -> None:
            captured_settings.append(ctx.obj["settings"])

        runner.invoke(cmd, ["--config", str(config)])

        assert captured_settings[0].debug is True

    def test_cli_overrides_config_file(self, runner: CliRunner, tmp_path: Path) -> None:
        """CLI options override config file values."""
        config = tmp_path / "config.yaml"
        config.write_text("debug: true\nlog_level: ERROR\n")
        captured_settings = []

        @click.command()
        @buvis_options
        @click.pass_context
        def cmd(ctx: click.Context) -> None:
            captured_settings.append(ctx.obj["settings"])

        runner.invoke(cmd, ["--config", str(config), "--no-debug"])

        assert captured_settings[0].debug is False
        assert captured_settings[0].log_level == "ERROR"


class TestGetSettings:
    """Tests for get_settings helper function."""

    def test_returns_settings_from_context(self, runner: CliRunner) -> None:
        """get_settings returns settings from ctx.obj."""
        captured = []

        @click.command()
        @buvis_options
        @click.pass_context
        def cmd(ctx: click.Context) -> None:
            settings = get_settings(ctx)
            captured.append(settings)

        runner.invoke(cmd, [])

        assert len(captured) == 1
        assert isinstance(captured[0], BuvisSettings)

    def test_returns_same_object_as_context(self, runner: CliRunner) -> None:
        """get_settings returns identical object to ctx.obj['settings']."""
        captured = []

        @click.command()
        @buvis_options
        @click.pass_context
        def cmd(ctx: click.Context) -> None:
            captured.append((ctx.obj["settings"], get_settings(ctx)))

        runner.invoke(cmd, [])

        assert captured[0][0] is captured[0][1]

    def test_raises_when_ctx_obj_none(self) -> None:
        """RuntimeError raised when ctx.obj is None."""
        from unittest.mock import MagicMock

        ctx = MagicMock(spec=click.Context)
        ctx.obj = None

        with pytest.raises(RuntimeError, match="buvis_options decorator not applied"):
            get_settings(ctx)

    def test_raises_when_settings_key_missing(self) -> None:
        """RuntimeError raised when 'settings' key missing."""
        from unittest.mock import MagicMock

        ctx = MagicMock(spec=click.Context)
        ctx.obj = {}

        with pytest.raises(RuntimeError, match="buvis_options decorator not applied"):
            get_settings(ctx)

    def test_raises_when_ctx_obj_has_other_keys(self) -> None:
        """RuntimeError raised when ctx.obj has other keys but not 'settings'."""
        from unittest.mock import MagicMock

        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"other": "value"}

        with pytest.raises(RuntimeError, match="buvis_options decorator not applied"):
            get_settings(ctx)
