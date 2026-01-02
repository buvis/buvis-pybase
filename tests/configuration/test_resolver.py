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


class TestConfigResolverResolve:
    def test_resolve_applies_cli_overrides(self, monkeypatch) -> None:
        calls: dict[str, str | None] = {}

        def fake_find_config_files(tool_name: str | None = None) -> list[str]:
            calls["tool_name"] = tool_name
            return ["config.yaml"]

        monkeypatch.setattr(
            ConfigurationLoader,
            "find_config_files",
            staticmethod(fake_find_config_files),
        )

        overrides = {"debug": True, "log_level": "DEBUG"}
        resolver = ConfigResolver(tool_name="cli")
        settings = resolver.resolve(BuvisSettings, cli_overrides=overrides)

        assert calls["tool_name"] == "cli"
        assert settings.debug is True
        assert settings.log_level == "DEBUG"

    def test_resolve_sets_config_dir_env(self, monkeypatch) -> None:
        def fake_find_config_files(tool_name: str | None = None) -> list[str]:
            return []

        monkeypatch.setattr(
            ConfigurationLoader,
            "find_config_files",
            staticmethod(fake_find_config_files),
        )
        monkeypatch.delenv("BUVIS_CONFIG_DIR", raising=False)

        resolver = ConfigResolver()
        config_dir = "/tmp/buvis"
        resolver.resolve(BuvisSettings, config_dir=config_dir)

        assert os.environ["BUVIS_CONFIG_DIR"] == config_dir


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
