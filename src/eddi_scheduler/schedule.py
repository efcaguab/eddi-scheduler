"""Schedule logic for the eddi device controller."""

from datetime import datetime


# Weekday off-periods (hour ranges where device should be OFF).
# Each tuple is (stop_hour, start_hour) meaning: stop at stop_hour, start at start_hour.
WEEKDAY_OFF_PERIODS = [
    (6, 11),   # OFF from 6 AM, back ON at 11 AM
    (16, 22),  # OFF from 4 PM, back ON at 10 PM
]


def get_scheduled_command(now: datetime) -> str | None:
    """Return 'start', 'stop', or None based on the given NZ datetime.

    Schedule:
    - Weekdays (Mon-Fri): OFF from 6 AM until 11 AM, OFF from 4 PM until 10 PM.
      ON all other weekday hours.
    - Weekends (Sat-Sun): ON the entire time.
    - Defensive: Saturday at 6 AM issues a start to guard against missed Friday transitions.
    """
    hour = now.hour
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    is_weekday = weekday in range(5)

    if is_weekday:
        for stop_hour, start_hour in WEEKDAY_OFF_PERIODS:
            if hour == stop_hour:
                return "stop"
            if hour == start_hour:
                return "start"

    # Defensive weekend start: re-assert ON state Saturday morning
    if weekday == 5 and hour == 6:
        return "start"

    return None
