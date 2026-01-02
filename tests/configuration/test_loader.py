from __future__ import annotations

import inspect
import types
import pytest

from pathlib import Path

from buvis.pybase.configuration.loader import (
    ConfigurationLoader,
    _ENV_PATTERN,
    _substitute,
)


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


class TestSubstitute:
    """Tests for _substitute env var replacement."""

    def test_var_set_substituted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """${VAR} with VAR set -> value substituted."""
        monkeypatch.setenv("DB_HOST", "localhost")

        result, missing = _substitute("host: ${DB_HOST}")

        assert result == "host: localhost"
        assert missing == []

    def test_var_unset_tracked_in_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """${VAR} with VAR unset -> tracked in missing list."""
        monkeypatch.delenv("UNSET_VAR", raising=False)

        result, missing = _substitute("key: ${UNSET_VAR}")

        assert result == "key: ${UNSET_VAR}"  # Kept for error msg
        assert missing == ["UNSET_VAR"]

    def test_var_unset_uses_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """${VAR:-default} with VAR unset -> uses default."""
        monkeypatch.delenv("DB_PORT", raising=False)

        result, missing = _substitute("port: ${DB_PORT:-5432}")

        assert result == "port: 5432"
        assert missing == []

    def test_var_set_ignores_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """${VAR:-default} with VAR set -> uses VAR value."""
        monkeypatch.setenv("DB_PORT", "3306")

        result, missing = _substitute("port: ${DB_PORT:-5432}")

        assert result == "port: 3306"
        assert missing == []

    def test_nested_not_expanded(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Env value containing ${} is NOT re-processed."""
        monkeypatch.setenv("VAR", "${NESTED}")

        result, missing = _substitute("val: ${VAR}")

        assert result == "val: ${NESTED}"  # Literal, not expanded
        assert missing == []

    def test_multiple_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Multiple vars in same content all substituted."""
        monkeypatch.setenv("HOST", "localhost")
        monkeypatch.setenv("PORT", "5432")

        result, missing = _substitute("url: ${HOST}:${PORT}")

        assert result == "url: localhost:5432"
        assert missing == []

    def test_multiple_missing_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Multiple missing vars all tracked."""
        monkeypatch.delenv("VAR1", raising=False)
        monkeypatch.delenv("VAR2", raising=False)

        result, missing = _substitute("a: ${VAR1}, b: ${VAR2}")

        assert missing == ["VAR1", "VAR2"]


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


class TestGetCandidateFiles:
    def test_empty_paths_returns_empty(self) -> None:
        result = ConfigurationLoader._get_candidate_files([], None)

        assert result == []

    def test_single_path_no_tool(self) -> None:
        result = ConfigurationLoader._get_candidate_files([Path("/cfg")], None)

        assert result == [Path("/cfg/buvis.yaml")]

    def test_multiple_paths_no_tool(self) -> None:
        paths = [Path("/a"), Path("/b")]

        result = ConfigurationLoader._get_candidate_files(paths, None)

        assert result == [Path("/a/buvis.yaml"), Path("/b/buvis.yaml")]

    def test_single_path_with_tool(self) -> None:
        result = ConfigurationLoader._get_candidate_files([Path("/cfg")], "payroll")

        assert result == [Path("/cfg/buvis.yaml"), Path("/cfg/buvis-payroll.yaml")]

    def test_multiple_paths_with_tool_maintains_interleaved_order(self) -> None:
        paths = [Path("/a"), Path("/b")]

        result = ConfigurationLoader._get_candidate_files(paths, "myapp")

        expected = [
            Path("/a/buvis.yaml"),
            Path("/a/buvis-myapp.yaml"),
            Path("/b/buvis.yaml"),
            Path("/b/buvis-myapp.yaml"),
        ]
        assert result == expected

    def test_empty_string_tool_name_treated_as_no_tool(self) -> None:
        result = ConfigurationLoader._get_candidate_files([Path("/cfg")], "")

        assert result == [Path("/cfg/buvis.yaml")]
