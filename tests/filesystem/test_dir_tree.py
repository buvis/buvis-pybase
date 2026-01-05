from __future__ import annotations

import platform  # noqa: F401
from pathlib import Path

import pytest

from buvis.pybase.filesystem import DirTree  # noqa: F401


@pytest.fixture
def nested_dir(tmp_path: Path) -> Path:
    """Create nested directory structure for testing."""
    (tmp_path / "level1" / "level2" / "level3").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def files_dir(tmp_path: Path) -> Path:
    """Create directory with various files."""
    (tmp_path / "file1.txt").touch()
    (tmp_path / "file2.log").touch()
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "file3.txt").touch()
    return tmp_path


class TestCountFiles:
    pass


class TestGetMaxDepth:
    pass
