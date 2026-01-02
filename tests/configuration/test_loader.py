from __future__ import annotations

import inspect
import types
import pytest

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
