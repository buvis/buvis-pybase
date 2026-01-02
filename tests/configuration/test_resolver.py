from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from buvis.pybase.configuration.buvis_settings import BuvisSettings
from buvis.pybase.configuration.loader import ConfigurationLoader
from buvis.pybase.configuration.resolver import ConfigResolver, _load_yaml_config


class TestConfigResolverInit:
    def test_instantiation_without_tool_name(self) -> None:
        resolver = ConfigResolver()

        assert resolver.tool_name is None
        assert isinstance(resolver.loader, ConfigurationLoader)

    def test_instantiation_with_tool_name(self) -> None:
        resolver = ConfigResolver(tool_name="cli")

        assert resolver.tool_name == "cli"
        assert isinstance(resolver.loader, ConfigurationLoader)

    def test_valid_lowercase_tool_name(self) -> None:
        """Lowercase tool_name without hyphens is accepted."""
        resolver = ConfigResolver(tool_name="payroll")

        assert resolver.tool_name == "payroll"

    def test_uppercase_tool_name_raises(self) -> None:
        """Uppercase in tool_name raises ValueError."""
        with pytest.raises(ValueError, match="lowercase"):
            ConfigResolver(tool_name="PayRoll")

    def test_hyphen_tool_name_raises(self) -> None:
        """Hyphen in tool_name raises ValueError."""
        with pytest.raises(ValueError, match="hyphens"):
            ConfigResolver(tool_name="pay-roll")

    def test_underscore_tool_name_allowed(self) -> None:
        """Underscore in tool_name is allowed."""
        resolver = ConfigResolver(tool_name="my_tool")

        assert resolver.tool_name == "my_tool"


class TestConfigResolverResolve:
    def test_resolve_applies_cli_overrides(self) -> None:
        """CLI overrides are applied to settings."""
        overrides = {"debug": True, "log_level": "DEBUG"}
        resolver = ConfigResolver(tool_name="cli")

        settings = resolver.resolve(BuvisSettings, cli_overrides=overrides)

        assert settings.debug is True
        assert settings.log_level == "DEBUG"

    def test_resolve_sets_config_dir_env(self, monkeypatch) -> None:
        monkeypatch.delenv("BUVIS_CONFIG_DIR", raising=False)

        resolver = ConfigResolver()
        config_dir = "/tmp/buvis"
        resolver.resolve(BuvisSettings, config_dir=config_dir)

        assert os.environ["BUVIS_CONFIG_DIR"] == config_dir


class TestConfigResolverPrecedence:
    """Tests for CLI > ENV > YAML > Defaults precedence."""

    def test_cli_wins_when_all_sources_set(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """CLI overrides take precedence over ENV and YAML."""
        config = tmp_path / "config.yaml"
        config.write_text("debug: false\nlog_level: WARNING\n")
        monkeypatch.setenv("BUVIS_DEBUG", "false")
        monkeypatch.setenv("BUVIS_LOG_LEVEL", "ERROR")

        resolver = ConfigResolver()
        settings = resolver.resolve(
            BuvisSettings,
            config_path=config,
            cli_overrides={"debug": True, "log_level": "DEBUG"},
        )

        assert settings.debug is True
        assert settings.log_level == "DEBUG"

    def test_env_wins_when_no_cli(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ENV overrides YAML when no CLI provided."""
        config = tmp_path / "config.yaml"
        config.write_text("debug: false\nlog_level: WARNING\n")
        monkeypatch.setenv("BUVIS_DEBUG", "true")
        monkeypatch.setenv("BUVIS_LOG_LEVEL", "ERROR")

        resolver = ConfigResolver()
        settings = resolver.resolve(BuvisSettings, config_path=config)

        assert settings.debug is True
        assert settings.log_level == "ERROR"

    def test_yaml_wins_when_no_cli_or_env(self, tmp_path: Path) -> None:
        """YAML overrides defaults when no CLI or ENV."""
        config = tmp_path / "config.yaml"
        config.write_text("debug: true\nlog_level: WARNING\n")

        resolver = ConfigResolver()
        settings = resolver.resolve(BuvisSettings, config_path=config)

        assert settings.debug is True
        assert settings.log_level == "WARNING"

    def test_default_used_when_only_default(self) -> None:
        """Defaults used when no other sources set values."""
        resolver = ConfigResolver()

        settings = resolver.resolve(BuvisSettings)

        assert settings.debug is False
        assert settings.log_level == "INFO"

    def test_cli_none_falls_through(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """CLI=None falls through to ENV value."""
        config = tmp_path / "config.yaml"
        config.write_text("debug: false\n")
        monkeypatch.setenv("BUVIS_DEBUG", "true")

        resolver = ConfigResolver()
        settings = resolver.resolve(
            BuvisSettings,
            config_path=config,
            cli_overrides={"debug": None},
        )

        # None in CLI means "not provided", so ENV wins
        assert settings.debug is True


class TestLoadYamlConfig:
    """Tests for _load_yaml_config function."""

    def test_valid_yaml_returns_dict(self, tmp_path: Path) -> None:
        """Valid YAML file returns parsed dict."""
        config = tmp_path / "config.yaml"
        config.write_text("debug: true\nlog_level: DEBUG\n")

        result = _load_yaml_config(config)

        assert result == {"debug": True, "log_level": "DEBUG"}

    def test_missing_file_returns_empty_dict(self, tmp_path: Path) -> None:
        """Missing file returns empty dict."""
        missing = tmp_path / "nonexistent.yaml"

        result = _load_yaml_config(missing)

        assert result == {}

    def test_empty_file_returns_empty_dict(self, tmp_path: Path) -> None:
        """Empty file returns empty dict."""
        empty = tmp_path / "empty.yaml"
        empty.write_text("")

        result = _load_yaml_config(empty)

        assert result == {}

    def test_invalid_yaml_raises(self, tmp_path: Path) -> None:
        """Invalid YAML raises exception."""
        invalid = tmp_path / "invalid.yaml"
        invalid.write_text("key: [broken")

        with pytest.raises(yaml.YAMLError):
            _load_yaml_config(invalid)

    def test_env_var_override(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """BUVIS_CONFIG_FILE env var takes precedence."""
        config = tmp_path / "custom.yaml"
        config.write_text("custom: true\n")
        monkeypatch.setenv("BUVIS_CONFIG_FILE", str(config))

        result = _load_yaml_config()

        assert result == {"custom": True}

    def test_explicit_path_param(self, tmp_path: Path) -> None:
        """Explicit file_path param is used."""
        config = tmp_path / "explicit.yaml"
        config.write_text("explicit: yes\n")

        result = _load_yaml_config(config)

        assert result == {"explicit": True}
