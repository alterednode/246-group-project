"""
Clock mapping 

- Uses FULL-STEP motor mode
- Computes SHORTEST rotation (forward or backward)
- Returns:
    steps (int)         -> always positive
    clockwise (bool)    -> True = forward, False = backward
"""

# 2048 steps for one full rotation of motor.

# Updated for FULL-STEP motor
STEPS_PER_FULL_CLOCK_CYCLE = 33636

# 12 hours = 720 minutes
MINUTES_PER_FULL_CLOCK_CYCLE = 720
HALF_CLOCK_CYCLE = MINUTES_PER_FULL_CLOCK_CYCLE // 2  # 360


def time_to_total_minutes(hour, minute):
    """
    Convert time to minutes on a 12-hour clock.
    """
    hour = hour % 12
    return hour * 60 + minute


def minutes_to_steps(minutes):
    """
    Convert minutes of movement into motor steps.
    """
    steps_per_minute = STEPS_PER_FULL_CLOCK_CYCLE / MINUTES_PER_FULL_CLOCK_CYCLE
    return round(minutes * steps_per_minute)


def time_delta_minutes(current_hour, current_minute, target_hour, target_minute):
    """
    Compute shortest time difference (in minutes).
    Positive  -> forward
    Negative  -> backward
    """
    current_total = time_to_total_minutes(current_hour, current_minute)
    target_total = time_to_total_minutes(target_hour, target_minute)

    diff = target_total - current_total

    if diff > HALF_CLOCK_CYCLE:
        diff -= MINUTES_PER_FULL_CLOCK_CYCLE
    elif diff < -HALF_CLOCK_CYCLE:
        diff += MINUTES_PER_FULL_CLOCK_CYCLE

    return diff


def time_delta_to_steps(current_hour, current_minute, target_hour, target_minute):
    """
    Convert time difference into:
    - step count
    - direction boolean
    """
    delta_minutes = time_delta_minutes(
        current_hour,
        current_minute,
        target_hour,
        target_minute
    )

    clockwise = delta_minutes >= 0
    steps = minutes_to_steps(abs(delta_minutes))

    return steps, clockwise

