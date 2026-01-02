from __future__ import annotations

import inspect
import types
import pytest

from buvis.pybase.configuration.loader import ConfigurationLoader


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
