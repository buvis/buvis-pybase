"""Tests for OutlookLocal exceptions (platform-independent).

Note: These tests exec the exceptions.py file directly to avoid triggering
the OS check in the outlook_local __init__.py which imports the adapter.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# Execute the exceptions module directly without going through the package __init__.py
_exceptions_path = (
    Path(__file__).parent.parent.parent
    / "src"
    / "buvis"
    / "pybase"
    / "adapters"
    / "outlook_local"
    / "exceptions.py"
)
_namespace: dict = {}
exec(_exceptions_path.read_text(), _namespace)
OutlookAppointmentCreationFailedError = _namespace[
    "OutlookAppointmentCreationFailedError"
]


class TestOutlookExceptions:
    """Tests for OutlookAppointmentCreationFailedError."""

    def test_exception_default_message(self) -> None:
        """Exception uses default message when none provided."""
        exc = OutlookAppointmentCreationFailedError()
        assert str(exc) == "Appointment not created in Outlook."

    def test_exception_custom_message(self) -> None:
        """Exception accepts custom message."""
        msg = "Custom error message"
        exc = OutlookAppointmentCreationFailedError(msg)
        assert str(exc) == msg

    def test_exception_is_exception_subclass(self) -> None:
        """Exception inherits from Exception."""
        assert issubclass(OutlookAppointmentCreationFailedError, Exception)

    def test_exception_can_be_raised_and_caught(self) -> None:
        """Exception can be raised and caught."""
        with pytest.raises(OutlookAppointmentCreationFailedError):
            raise OutlookAppointmentCreationFailedError("test")
