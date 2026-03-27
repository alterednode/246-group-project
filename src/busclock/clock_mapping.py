from __future__ import annotations

from datetime import datetime, tzinfo

"""
Converts a leave time into the number of motor steps required
to rotate the clock from the reset position (12:00) to the
correct display time.

Assumptions:
1) The clock resets to 12:00 before each update
2) 28BYJ-48 stepper motor (4096 steps per revolution)
"""

# Calculate this in the lab
STEPS_PER_FULL_CLOCK_CYCLE = 5715   # motor steps for 12 hours

# 12 hours = 720 minutes
MINUTES_PER_FULL_CLOCK_CYCLE = 720


def time_to_total_minutes(hour: int, minute: int) -> int:

    hour = hour % 12  # Handles 24-hour time inputs
    return hour * 60 + minute


def min_to_steps(minute: int) -> int:
    steps_per_minute = STEPS_PER_FULL_CLOCK_CYCLE / MINUTES_PER_FULL_CLOCK_CYCLE
    return round(minute * steps_per_minute)


def time_to_motor_steps(hour: int, minute: int) -> int:
    """
    Converts a clock time into motor steps
    starting from the reset position (12:00).
    """

    total_minutes = time_to_total_minutes(hour, minute)

    steps_per_minute = STEPS_PER_FULL_CLOCK_CYCLE / MINUTES_PER_FULL_CLOCK_CYCLE

    steps = round(total_minutes * steps_per_minute)

    return steps

