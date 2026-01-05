from __future__ import annotations

import platform  # noqa: F401
from pathlib import Path

import pytest

from buvis.pybase.filesystem import DirTree


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
    def test_counts_files_in_flat_directory(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").touch()
        (tmp_path / "b.txt").touch()
        assert DirTree.count_files(tmp_path) == 2

    def test_counts_files_recursively(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").touch()
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "b.txt").touch()
        assert DirTree.count_files(tmp_path) == 2

    def test_returns_zero_for_empty_directory(self, tmp_path: Path) -> None:
        assert DirTree.count_files(tmp_path) == 0

    def test_excludes_directories_from_count(self, tmp_path: Path) -> None:
        (tmp_path / "dir").mkdir()
        (tmp_path / "file.txt").touch()
        assert DirTree.count_files(tmp_path) == 1


class TestGetMaxDepth:
    pass
