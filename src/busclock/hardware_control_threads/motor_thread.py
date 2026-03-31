from __future__ import annotations

import logging
import threading
from datetime import datetime

from ..clock_mapping import STEPS_PER_FULL_CLOCK_CYCLE, time_delta_to_steps
from ..state import StateStore

LOGGER = logging.getLogger(__name__)
SECONDS_PER_CLOCK_CYCLE = 12 * 60 * 60
POLL_INTERVAL_SECONDS = 0.25

def run_motor_thread(
    *,
    state_store: StateStore,
    stop_event: threading.Event,
) -> None:
    LOGGER.debug(
        "Motor thread starting with poll_interval=%ss steps_per_cycle=%s",
        POLL_INTERVAL_SECONDS,
        STEPS_PER_FULL_CLOCK_CYCLE,
    )
    motor = None
    try:
        from ..electronics.motor import MotorControl
    except Exception as exc:
        LOGGER.info("Motor controller unavailable; motor thread running without GPIO: %s", exc)
    else:
        try:
            motor = MotorControl()
            LOGGER.debug("Motor controller initialized successfully")
        except Exception as exc:
            LOGGER.warning(
                "Motor controller initialization failed; motor thread running without GPIO: %s",
                exc,
                exc_info=True,
            )
    curr_num_steps = 0
    curr_displayed_seconds = 0  # 12:00:00 at thread start.

    try:
        while not stop_event.is_set():
            state = state_store.snapshot()
            transit_status = state.status.get("transit")
            target_display_seconds = _target_display_seconds(state.transit.leave_at)
            LOGGER.debug(
                (
                    "Motor poll: transit_status=%s leave_at=%s minutes_until_leave=%s "
                    "current_display=%s current_steps=%s target_display=%s"
                ),
                transit_status.state if transit_status else None,
                state.transit.leave_at.isoformat() if state.transit.leave_at else None,
                state.transit.minutes_until_leave,
                _format_clock_seconds(curr_displayed_seconds),
                curr_num_steps,
                _format_clock_seconds(target_display_seconds),
            )
            if target_display_seconds is None:
                LOGGER.debug("Skipping motor update because no leave_at target is available")
                stop_event.wait(POLL_INTERVAL_SECONDS)
                continue

            signed_steps = _steps_to_target(
                current_display_seconds=curr_displayed_seconds,
                target_display_seconds=target_display_seconds,
            )
            LOGGER.debug(
                "Motor target computed: current=%s target=%s signed_steps=%s",
                _format_clock_seconds(curr_displayed_seconds),
                _format_clock_seconds(target_display_seconds),
                signed_steps,
            )
            if signed_steps != 0:
                LOGGER.debug(
                    "Executing motor movement: signed_steps=%s direction=%s motor_available=%s",
                    signed_steps,
                    "clockwise" if signed_steps > 0 else "counterclockwise",
                    motor is not None,
                )
                if motor is not None:
                    motor.step(signed_steps)
                curr_num_steps = (curr_num_steps + signed_steps) % STEPS_PER_FULL_CLOCK_CYCLE
                curr_displayed_seconds = target_display_seconds
                LOGGER.debug(
                    "Updated motor display to leave_at=%s steps=%s position=%s",
                    state.transit.leave_at.isoformat() if state.transit.leave_at else None,
                    signed_steps,
                    curr_num_steps,
                )
            else:
                LOGGER.debug("Motor display already aligned with target; no movement required")

            stop_event.wait(POLL_INTERVAL_SECONDS)
    finally:
        LOGGER.debug(
            "Motor thread stopping with final_display=%s final_steps=%s",
            _format_clock_seconds(curr_displayed_seconds),
            curr_num_steps,
        )
        if motor is not None:
            LOGGER.debug("Cleaning up motor controller")
            motor.cleanup()



def _target_display_seconds(leave_at: datetime | None) -> int | None:
    if leave_at is None:
        return None
    return _seconds_on_clock_face(leave_at)


def _steps_to_target(
    *,
    current_display_seconds: int,
    target_display_seconds: int,
) -> int:
    current_hour, current_minute = _seconds_to_hour_minute(current_display_seconds)
    target_hour, target_minute = _seconds_to_hour_minute(target_display_seconds)
    steps, clockwise = time_delta_to_steps(
        current_hour,
        current_minute,
        target_hour,
        target_minute,
    )
    return steps if clockwise else -steps


def _seconds_on_clock_face(value: datetime) -> int:
    if value.tzinfo is not None:
        value = value.astimezone()
    return ((value.hour % 12) * 3600) + (value.minute * 60) + value.second


def _seconds_to_hour_minute(value: int) -> tuple[int, int]:
    normalized = value % SECONDS_PER_CLOCK_CYCLE
    total_minutes = normalized // 60
    return (total_minutes // 60) % 12, total_minutes % 60


def _format_clock_seconds(value: int | None) -> str | None:
    if value is None:
        return None
    normalized = value % SECONDS_PER_CLOCK_CYCLE
    hour = (normalized // 3600) % 12
    minute = (normalized % 3600) // 60
    second = normalized % 60
    return f"{hour:02d}:{minute:02d}:{second:02d}"
