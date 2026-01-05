from __future__ import annotations

import subprocess  # noqa: F401
from datetime import datetime, timezone  # noqa: F401
from pathlib import Path  # noqa: F401
from unittest.mock import Mock, patch  # noqa: F401

import pytest  # noqa: F401

from buvis.pybase.filesystem import FileMetadataReader  # noqa: F401


class TestGetCreationDatetime:
    """Tests for FileMetadataReader.get_creation_datetime."""

    @patch("buvis.pybase.filesystem.file_metadata.file_metadata_reader.platform.system")
    def test_uses_st_ctime_on_windows(self, mock_system: Mock, tmp_path: Path) -> None:
        mock_system.return_value = "Windows"
        file = tmp_path / "test.txt"
        file.touch()
        result = FileMetadataReader.get_creation_datetime(file)
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    @patch("buvis.pybase.filesystem.file_metadata.file_metadata_reader.platform.system")
    def test_uses_st_birthtime_on_macos(
        self, mock_system: Mock, tmp_path: Path
    ) -> None:
        mock_system.return_value = "Darwin"
        file = tmp_path / "test.txt"
        file.touch()
        result = FileMetadataReader.get_creation_datetime(file)
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    @patch("buvis.pybase.filesystem.file_metadata.file_metadata_reader.platform.system")
    def test_falls_back_to_st_mtime_when_no_birthtime(
        self, mock_system: Mock, tmp_path: Path
    ) -> None:
        """Linux doesn't have st_birthtime, falls back to st_mtime."""
        mock_system.return_value = "Linux"
        file = tmp_path / "test.txt"
        file.touch()

        original_stat = file.stat

        def mock_stat(self):
            stat_result = original_stat()
            mock_result = Mock(spec=[])
            mock_result.st_mtime = stat_result.st_mtime
            mock_result.st_ctime = stat_result.st_ctime
            return mock_result

        with patch.object(type(file), "stat", mock_stat):
            result = FileMetadataReader.get_creation_datetime(file)

        assert isinstance(result, datetime)
        assert result.tzinfo is not None


class TestGetFirstCommitDatetime:
    """Tests for FileMetadataReader.get_first_commit_datetime."""

    pass
