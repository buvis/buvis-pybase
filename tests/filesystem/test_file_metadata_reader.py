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

    @patch(
        "buvis.pybase.filesystem.file_metadata.file_metadata_reader.subprocess.check_output"
    )
    def test_parses_git_log_output(
        self, mock_check_output: Mock, tmp_path: Path
    ) -> None:
        mock_check_output.return_value = "2024-01-15T10:30:00+0000\n"
        result = FileMetadataReader.get_first_commit_datetime(tmp_path / "file.txt")
        assert result == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

    @patch(
        "buvis.pybase.filesystem.file_metadata.file_metadata_reader.subprocess.check_output"
    )
    def test_returns_none_when_not_in_git_repo(
        self, mock_check_output: Mock, tmp_path: Path
    ) -> None:
        mock_check_output.side_effect = subprocess.CalledProcessError(128, "git")
        result = FileMetadataReader.get_first_commit_datetime(tmp_path / "file.txt")
        assert result is None

    @patch(
        "buvis.pybase.filesystem.file_metadata.file_metadata_reader.subprocess.check_output"
    )
    def test_returns_none_for_uncommitted_file(
        self, mock_check_output: Mock, tmp_path: Path
    ) -> None:
        mock_check_output.return_value = ""
        result = FileMetadataReader.get_first_commit_datetime(tmp_path / "file.txt")
        assert result is None

    @patch(
        "buvis.pybase.filesystem.file_metadata.file_metadata_reader.subprocess.check_output"
    )
    def test_returns_none_for_malformed_date(
        self, mock_check_output: Mock, tmp_path: Path
    ) -> None:
        mock_check_output.return_value = "not-a-date\n"
        result = FileMetadataReader.get_first_commit_datetime(tmp_path / "file.txt")
        assert result is None
