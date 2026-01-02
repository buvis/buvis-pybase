from __future__ import annotations

import inspect
import types
import pytest

from pathlib import Path

from buvis.pybase.configuration.loader import ConfigurationLoader, _ENV_PATTERN


class TestConfigurationLoaderScaffold:
    def test_class_exists(self) -> None:
        assert inspect.isclass(ConfigurationLoader)

    def test_find_config_files_exists(self) -> None:
        assert hasattr(ConfigurationLoader, "find_config_files")
        assert isinstance(ConfigurationLoader.find_config_files, types.FunctionType)

    def test_find_config_files_with_tool_name(self) -> None:
        with pytest.raises(NotImplementedError):
            ConfigurationLoader.find_config_files(tool_name="test")

    def test_find_config_files_without_args(self) -> None:
        with pytest.raises(NotImplementedError):
            ConfigurationLoader.find_config_files()


class TestEnvPattern:
    def test_matches_variable(self) -> None:
        match = _ENV_PATTERN.fullmatch("${VAR}")
        assert match is not None
        assert match.group(1) == "VAR"
        assert match.group(2) is None

    def test_matches_variable_with_default(self) -> None:
        match = _ENV_PATTERN.fullmatch("${VAR:-default}")
        assert match is not None
        assert match.group(1) == "VAR"
        assert match.group(2) == "default"


class TestGetSearchPaths:
    def test_all_env_vars_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUVIS_CONFIG_DIR", "/custom/config")
        monkeypatch.setenv("XDG_CONFIG_HOME", "/custom/xdg")

        paths = ConfigurationLoader._get_search_paths()

        assert len(paths) == 4
        assert paths[0] == Path("/custom/config")
        assert paths[1] == Path("/custom/xdg/buvis")

    def test_buvis_config_dir_empty_string(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("BUVIS_CONFIG_DIR", "")
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)

        paths = ConfigurationLoader._get_search_paths()

        # Empty BUVIS_CONFIG_DIR treated as unset, so 3 paths
        assert len(paths) == 3
        assert paths[0] == Path.home() / ".config" / "buvis"

    def test_xdg_config_home_empty_fallback(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("BUVIS_CONFIG_DIR", raising=False)
        monkeypatch.setenv("XDG_CONFIG_HOME", "")

        paths = ConfigurationLoader._get_search_paths()

        assert paths[0] == Path.home() / ".config" / "buvis"

    def test_path_order_priority(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUVIS_CONFIG_DIR", "/override")
        monkeypatch.setenv("XDG_CONFIG_HOME", "/xdg")

        paths = ConfigurationLoader._get_search_paths()

        assert paths[0] == Path("/override")
        assert paths[1] == Path("/xdg/buvis")
        assert paths[2] == Path.home() / ".buvis"
        assert paths[3] == Path.cwd()

    def test_expanduser_tilde_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUVIS_CONFIG_DIR", "~/custom")
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)

        paths = ConfigurationLoader._get_search_paths()

        assert paths[0] == Path.home() / "custom"

    def test_legacy_buvis_always_present(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("BUVIS_CONFIG_DIR", raising=False)
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)

        paths = ConfigurationLoader._get_search_paths()

        assert Path.home() / ".buvis" in paths

    def test_cwd_always_last(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUVIS_CONFIG_DIR", "/override")

        paths = ConfigurationLoader._get_search_paths()

        assert paths[-1] == Path.cwd()
