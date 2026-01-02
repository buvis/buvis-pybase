from __future__ import annotations

import os

from buvis.pybase.configuration.buvis_settings import BuvisSettings
from buvis.pybase.configuration.loader import ConfigurationLoader
from buvis.pybase.configuration.resolver import ConfigResolver


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
