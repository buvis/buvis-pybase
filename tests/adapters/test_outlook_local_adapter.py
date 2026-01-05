"""Tests for OutlookLocalAdapter (Windows-only).

These tests are skipped on non-Windows platforms since the module
uses win32com which is Windows-specific.
"""

from __future__ import annotations

import sys
from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from buvis.pybase.adapters.outlook_local.outlook_local import OutlookLocalAdapter

pytestmark = pytest.mark.skipif(
    sys.platform != "win32",
    reason="OutlookLocalAdapter requires Windows",
)


@pytest.fixture
def mock_win32com() -> MagicMock:
    """Mock win32com.client.Dispatch for COM automation."""
    with patch("win32com.client.Dispatch") as mock_dispatch:
        mock_app = MagicMock()
        mock_namespace = MagicMock()
        mock_calendar = MagicMock()
        mock_app.GetNamespace.return_value = mock_namespace
        mock_namespace.GetDefaultFolder.return_value = mock_calendar
        mock_dispatch.return_value = mock_app
        yield mock_dispatch


@pytest.fixture
def outlook_adapter(mock_win32com: MagicMock) -> OutlookLocalAdapter:
    """Create an OutlookLocalAdapter instance with mocked COM objects."""
    from buvis.pybase.adapters.outlook_local.outlook_local import OutlookLocalAdapter

    return OutlookLocalAdapter()


class TestOutlookLocalAdapterInit:
    """Tests for OutlookLocalAdapter initialization."""

    def test_connects_to_outlook(self, mock_win32com: MagicMock) -> None:
        """Init connects to Outlook via COM and gets MAPI namespace."""
        from buvis.pybase.adapters.outlook_local.outlook_local import (
            OutlookLocalAdapter,
        )

        _adapter = OutlookLocalAdapter()

        mock_win32com.assert_called_once_with("Outlook.Application")
        mock_app = mock_win32com.return_value
        mock_app.GetNamespace.assert_called_once_with("MAPI")
        mock_namespace = mock_app.GetNamespace.return_value
        mock_namespace.GetDefaultFolder.assert_called_once_with(9)

    def test_panics_when_dispatch_fails(self) -> None:
        """Init calls console.panic when COM connection fails."""
        from buvis.pybase.adapters.outlook_local import outlook_local

        with (
            patch("win32com.client.Dispatch", side_effect=Exception("boom")),
            patch.object(
                outlook_local.console, "panic", side_effect=SystemExit
            ) as mock_panic,
        ):
            with pytest.raises(SystemExit):
                outlook_local.OutlookLocalAdapter()
            mock_panic.assert_called_once()


class TestCreateTimeblock:
    """Tests for create_timeblock method."""

    def test_sets_properties_with_explicit_start(
        self, outlook_adapter: OutlookLocalAdapter, mock_win32com: MagicMock
    ) -> None:
        """Creates appointment with provided start time."""
        mock_app = mock_win32com.return_value
        appointment = MagicMock()
        mock_app.CreateItem.return_value = appointment

        start = datetime(2024, 3, 15, 9, 0)
        outlook_adapter.create_timeblock(
            {
                "start": start,
                "subject": "Sync",
                "body": "Align work",
                "duration": 30,
                "location": "Desk",
                "categories": "Work",
            }
        )

        assert appointment.Start is start
        assert appointment.Subject == "Sync"
        assert appointment.Body == "Align work"
        assert appointment.Duration == 30
        assert appointment.Location == "Desk"
        assert appointment.Categories == "Work"
        appointment.Save.assert_called_once()

    def test_uses_current_time_when_start_missing(
        self, outlook_adapter: OutlookLocalAdapter, mock_win32com: MagicMock
    ) -> None:
        """Uses current hour when start time not provided."""
        from datetime import timezone

        from buvis.pybase.adapters.outlook_local import outlook_local

        mock_app = mock_win32com.return_value
        appointment = MagicMock()
        mock_app.CreateItem.return_value = appointment

        fake_now = datetime(2024, 3, 15, 9, 37, 22, tzinfo=timezone.utc)
        expected_start = fake_now.replace(minute=0, second=0)

        with (
            patch.object(
                outlook_local.tzlocal, "get_localzone", return_value=timezone.utc
            ),
            patch.object(outlook_local.datetime, "now", return_value=fake_now),
        ):
            outlook_adapter.create_timeblock(
                {
                    "subject": "Sync",
                    "body": "Align work",
                    "duration": 30,
                    "location": "Desk",
                    "categories": "Work",
                }
            )

        assert appointment.Start == expected_start
        appointment.Save.assert_called_once()

    def test_raises_on_save_failure(
        self, outlook_adapter: OutlookLocalAdapter, mock_win32com: MagicMock
    ) -> None:
        """Raises OutlookAppointmentCreationFailedError when save fails."""
        from buvis.pybase.adapters.outlook_local.exceptions import (
            OutlookAppointmentCreationFailedError,
        )

        mock_app = mock_win32com.return_value
        appointment = MagicMock()
        appointment.Save.side_effect = Exception("boom")
        mock_app.CreateItem.return_value = appointment

        with pytest.raises(OutlookAppointmentCreationFailedError) as excinfo:
            outlook_adapter.create_timeblock(
                {
                    "start": datetime(2024, 3, 15, 9, 0),
                    "subject": "Sync",
                    "body": "Align work",
                    "duration": 30,
                    "location": "Desk",
                    "categories": "Work",
                }
            )

        assert "Appointment creation failed" in str(excinfo.value)


class TestGetAppointments:
    """Tests for appointment retrieval methods."""

    def test_get_all_appointments_includes_recurrences(
        self, outlook_adapter: OutlookLocalAdapter
    ) -> None:
        """Returns calendar items with recurrences included and sorted."""
        items = MagicMock()
        outlook_adapter.calendar.Items = items

        result = outlook_adapter.get_all_appointments()

        assert result is items
        assert items.IncludeRecurrences is True
        items.Sort.assert_called_once_with("[Start]")

    def test_get_day_appointments_filters_by_date(
        self, outlook_adapter: OutlookLocalAdapter
    ) -> None:
        """Restricts appointments to specified date."""
        appointments = MagicMock()

        matching = MagicMock()
        matching.Start = datetime(2024, 3, 15, 9, 0)

        non_matching = MagicMock()
        non_matching.Start = datetime(2024, 3, 16, 9, 0)

        appointments.Restrict.return_value = [matching, non_matching]
        date = datetime(2024, 3, 15, 12, 0)

        result = outlook_adapter.get_day_appointments(appointments, date)

        assert result == [matching]
        appointments.Restrict.assert_called_once_with(
            "[Start] >= '2024-03-15' AND [End] <= '2024-03-16'"
        )


class TestGetConflictingAppointment:
    """Tests for conflict detection."""

    def test_returns_conflicting_appointment(
        self, outlook_adapter: OutlookLocalAdapter
    ) -> None:
        """Returns appointment that conflicts with desired time slot."""
        from buvis.pybase.adapters.outlook_local import outlook_local

        appointment = MagicMock()
        appointment.Start = datetime(2024, 3, 15, 9, 30)
        appointment.End = datetime(2024, 3, 15, 10, 30)
        appointment.Subject = "Busy"

        desired_start = datetime(2024, 3, 15, 10, 0)

        with (
            patch.object(
                outlook_adapter, "get_all_appointments", return_value=MagicMock()
            ),
            patch.object(
                outlook_adapter, "get_day_appointments", return_value=[appointment]
            ),
            patch.object(outlook_local.console, "print"),
        ):
            result = outlook_adapter.get_conflicting_appointment(
                desired_start, 60, debug_level=1
            )

        assert result is appointment

    def test_returns_none_when_free(self, outlook_adapter: OutlookLocalAdapter) -> None:
        """Returns None when no conflicts exist."""
        appointment = MagicMock()
        appointment.Start = datetime(2024, 3, 15, 12, 0)
        appointment.End = datetime(2024, 3, 15, 13, 0)

        desired_start = datetime(2024, 3, 15, 10, 0)

        with (
            patch.object(
                outlook_adapter, "get_all_appointments", return_value=MagicMock()
            ),
            patch.object(
                outlook_adapter, "get_day_appointments", return_value=[appointment]
            ),
        ):
            result = outlook_adapter.get_conflicting_appointment(desired_start, 60)

        assert result is None


class TestIsColliding:
    """Tests for _is_colliding helper function."""

    def test_detects_overlap(self) -> None:
        """Returns True when time ranges overlap."""
        from buvis.pybase.adapters.outlook_local.outlook_local import _is_colliding

        assert _is_colliding(
            datetime(2024, 3, 15, 9, 0),
            datetime(2024, 3, 15, 10, 0),
            datetime(2024, 3, 15, 9, 30),
            datetime(2024, 3, 15, 9, 45),
        )

    def test_detects_no_overlap(self) -> None:
        """Returns False when time ranges don't overlap."""
        from buvis.pybase.adapters.outlook_local.outlook_local import _is_colliding

        assert not _is_colliding(
            datetime(2024, 3, 15, 9, 0),
            datetime(2024, 3, 15, 10, 0),
            datetime(2024, 3, 15, 10, 0),
            datetime(2024, 3, 15, 11, 0),
        )
