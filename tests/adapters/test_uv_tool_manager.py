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

    pass
