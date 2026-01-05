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
