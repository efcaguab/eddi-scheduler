"""Tests for the eddi schedule logic."""

import pytest
from datetime import datetime

import pytz

from eddi_scheduler.schedule import get_scheduled_command

NZ = pytz.timezone("Pacific/Auckland")


def _nz(year: int, month: int, day: int, hour: int) -> datetime:
    """Build a timezone-aware NZ datetime."""
    return NZ.localize(datetime(year, month, day, hour, 0, 0))


# --- Weekday boundary tests (Mon 2026-03-23) ---

class TestWeekdayMorningOffPeriod:
    def test_stop_at_6am(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 6)) == "stop"

    def test_start_at_11am(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 11)) == "start"

    def test_no_action_at_5am(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 5)) is None

    def test_no_action_at_7am(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 7)) is None

    def test_no_action_at_10am(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 10)) is None

    def test_no_action_at_noon(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 12)) is None


class TestWeekdayEveningOffPeriod:
    def test_stop_at_4pm(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 16)) == "stop"

    def test_start_at_10pm(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 22)) == "start"

    def test_no_action_at_3pm(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 15)) is None

    def test_no_action_at_5pm(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 17)) is None

    def test_no_action_at_9pm(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 21)) is None

    def test_no_action_at_11pm(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 23)) is None


class TestWeekdayNoAction:
    def test_midnight(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 0)) is None

    def test_1pm(self):
        assert get_scheduled_command(_nz(2026, 3, 23, 13)) is None


# --- All weekdays have the same schedule ---

class TestAllWeekdays:
    @pytest.mark.parametrize("day", [23, 24, 25, 26, 27])  # Mon-Fri 2026-03-23..27
    def test_stop_at_6am(self, day):
        assert get_scheduled_command(_nz(2026, 3, day, 6)) == "stop"

    @pytest.mark.parametrize("day", [23, 24, 25, 26, 27])
    def test_start_at_11am(self, day):
        assert get_scheduled_command(_nz(2026, 3, day, 11)) == "start"

    @pytest.mark.parametrize("day", [23, 24, 25, 26, 27])
    def test_stop_at_4pm(self, day):
        assert get_scheduled_command(_nz(2026, 3, day, 16)) == "stop"

    @pytest.mark.parametrize("day", [23, 24, 25, 26, 27])
    def test_start_at_10pm(self, day):
        assert get_scheduled_command(_nz(2026, 3, day, 22)) == "start"


# --- Weekend tests ---

class TestWeekend:
    # Saturday 2026-03-28
    def test_saturday_6am_defensive_start(self):
        assert get_scheduled_command(_nz(2026, 3, 28, 6)) == "start"

    def test_saturday_noon_no_action(self):
        assert get_scheduled_command(_nz(2026, 3, 28, 12)) is None

    def test_saturday_midnight_no_action(self):
        assert get_scheduled_command(_nz(2026, 3, 28, 0)) is None

    # Sunday 2026-03-29
    def test_sunday_6am_no_action(self):
        assert get_scheduled_command(_nz(2026, 3, 29, 6)) is None

    def test_sunday_noon_no_action(self):
        assert get_scheduled_command(_nz(2026, 3, 29, 12)) is None

    def test_sunday_11pm_no_action(self):
        assert get_scheduled_command(_nz(2026, 3, 29, 23)) is None


# --- Transition tests ---

class TestTransitions:
    def test_friday_10pm_starts(self):
        """Friday evening off-period ends, device stays ON into weekend."""
        # Friday 2026-03-27
        assert get_scheduled_command(_nz(2026, 3, 27, 22)) == "start"

    def test_monday_6am_stops(self):
        """First action after weekend is Monday morning stop."""
        # Monday 2026-03-23
        assert get_scheduled_command(_nz(2026, 3, 23, 6)) == "stop"
