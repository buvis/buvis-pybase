from __future__ import annotations

import os  # noqa: F401
import subprocess
import sys  # noqa: F401
from pathlib import Path  # noqa: F401
from unittest.mock import MagicMock, patch  # noqa: F401

import pytest  # noqa: F401

from buvis.pybase.adapters.uv.uv_tool import UvToolManager  # noqa: F401


@pytest.fixture
def mock_ensure_uv():
    """Mock UvAdapter.ensure_uv to skip uv installation check."""
    with patch("buvis.pybase.adapters.uv.uv_tool.UvAdapter.ensure_uv") as mock:
        yield mock


@pytest.fixture
def mock_console():
    """Mock console output methods."""
    with patch("buvis.pybase.adapters.uv.uv_tool.console") as mock:
        yield mock


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for command execution."""
    with patch("subprocess.run") as mock:
        mock.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        yield mock


class TestUvToolManager:
    """Tests for UvToolManager."""

    def test_installs_projects_with_pyproject_toml(
        self, mock_ensure_uv, mock_console, mock_subprocess_run, tmp_path
    ):
        """Should call install_tool for each dir with pyproject.toml."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create two projects with pyproject.toml
        for name in ["pkg_a", "pkg_b"]:
            project = src_dir / name
            project.mkdir()
            (project / "pyproject.toml").write_text("[project]")

        with patch.object(UvToolManager, "install_tool") as mock_install:
            UvToolManager.install_all(tmp_path)

        assert mock_install.call_count == 2
        mock_ensure_uv.assert_called_once()


class TestInstallTool:
    """Tests for UvToolManager.install_tool()."""

    def test_installs_tool_successfully(
        self, mock_console, mock_subprocess_run, tmp_path
    ):
        """Should run uv tool install with correct args."""
        project = tmp_path / "my_pkg"
        project.mkdir()
        (project / "pyproject.toml").write_text("[project]")

        UvToolManager.install_tool(project)

        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args[0][0]
        assert call_args[:3] == ["uv", "tool", "install"]
        assert "--force" in call_args
        assert "--upgrade" in call_args
        assert str(project) in call_args
        mock_console.success.assert_called_once()


class TestRun:
    """Tests for UvToolManager.run()."""

    def test_runs_via_uv_tool_run(self, mock_ensure_uv, mock_subprocess_run, tmp_path):
        """Should use uv tool run in normal mode."""
        script = tmp_path / "bin" / "my-tool"
        script.parent.mkdir(parents=True)
        script.write_text("#!/usr/bin/env python")

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit) as exc_info:
                UvToolManager.run(str(script), ["arg1", "arg2"])

        assert exc_info.value.code == 0
        call_args = mock_subprocess_run.call_args[0][0]
        assert call_args[:3] == ["uv", "tool", "run"]
        assert "my-tool" in call_args
        assert "arg1" in call_args
        assert "arg2" in call_args
