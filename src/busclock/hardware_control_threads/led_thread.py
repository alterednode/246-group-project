from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ..LED_management.RGB import RGB, blank_frame, num_leds
from ..state import StateStore, SystemState, WeatherSnapshot

LOGGER = logging.getLogger(__name__)

FRAME_INTERVAL_SECONDS = 0.25
FIVE_MINUTE_WARNING_SECONDS = 5 * 60
ONE_MINUTE_WARNING_SECONDS = 60

WARNING_FIVE_MINUTE = "warning_five_minutes"
WARNING_ONE_MINUTE = "warning_one_minute"
WEATHER_SUNNY = "weather_sunny"
WEATHER_CLOUDY = "weather_cloudy"
WEATHER_RAIN = "weather_rain"
WEATHER_SNOW = "weather_snow"

RAIN_STEPS: tuple[tuple[int, ...], ...] = (
    (3, 7, 11, 18, 22, 30),
    (19, 27, 29, 40, 54, 69),
    (42, 49, 55, 71, 83, 95),
    (51, 73, 81, 94, 98, 100),
)
SNOW_STEPS: tuple[tuple[int, ...], ...] = (
    (2, 6, 11, 18, 22, 25, 29),
    (20, 28, 38, 40, 44, 46, 69),
    (42, 53, 55, 65, 73, 75, 81),
    (50, 76, 79, 87, 94, 99, 105),
)


@dataclass(frozen=True, slots=True)
class AnimationSelection:
    mode: str
    reason: str


def run_led_thread(
    *,
    state_store: StateStore,
    stop_event: threading.Event,
) -> None:
    LOGGER.debug("LED thread starting with frame_interval=%ss", FRAME_INTERVAL_SECONDS)
    controller = _create_led_controller()
    active_selection: AnimationSelection | None = None
    step = 0

    try:
        while not stop_event.is_set():
            state = state_store.snapshot()
            selection = _select_animation(state)
            if selection != active_selection:
                LOGGER.info(
                    "LED animation changed to %s (%s)",
                    selection.mode,
                    selection.reason,
                )
                active_selection = selection
                step = 0

            frame = _build_frame(selection.mode, step)
            if controller is not None:
                controller.display(frame)

            step = (step + 1) % _animation_cycle_length(selection.mode)
            stop_event.wait(FRAME_INTERVAL_SECONDS)
    finally:
        LOGGER.debug("LED thread stopping")
        if controller is not None:
            controller.display(blank_frame())


def _create_led_controller() -> Any | None:
    try:
        from ..electronics.LEDs import LEDControl
    except Exception as exc:
        LOGGER.info("LED controller unavailable; LED thread running without GPIO: %s", exc)
        return None

    try:
        controller = LEDControl()
    except Exception as exc:
        LOGGER.warning(
            "LED controller initialization failed; LED thread running without GPIO: %s",
            exc,
            exc_info=True,
        )
        return None

    LOGGER.debug("LED controller initialized successfully")
    return controller


def _select_animation(
    state: SystemState,
    *,
    now: datetime | None = None,
) -> AnimationSelection:
    seconds_until_leave = _seconds_until_leave(state.transit.leave_at, now=now)
    if seconds_until_leave is not None:
        if seconds_until_leave <= ONE_MINUTE_WARNING_SECONDS:
            return AnimationSelection(
                mode=WARNING_ONE_MINUTE,
                reason=f"leave_at is {seconds_until_leave}s away",
            )
        if seconds_until_leave <= FIVE_MINUTE_WARNING_SECONDS:
            return AnimationSelection(
                mode=WARNING_FIVE_MINUTE,
                reason=f"leave_at is {seconds_until_leave}s away",
            )

    weather_mode = _weather_mode(state.weather)
    condition = state.weather.condition or "unknown"
    description = state.weather.description or "no description"
    return AnimationSelection(
        mode=weather_mode,
        reason=f"weather condition={condition!r} description={description!r}",
    )


def _seconds_until_leave(
    leave_at: datetime | None,
    *,
    now: datetime | None = None,
) -> int | None:
    if leave_at is None:
        return None
    reference = now or datetime.now(tz=leave_at.tzinfo or timezone.utc)
    return int((leave_at - reference).total_seconds())


def _weather_mode(weather: WeatherSnapshot) -> str:
    condition = (weather.condition or "").casefold()
    description = (weather.description or "").casefold()

    if weather.snow_1h_mm or weather.snow_3h_mm or condition == "snow" or "snow" in description:
        return WEATHER_SNOW
    if (
        weather.rain_1h_mm
        or weather.rain_3h_mm
        or condition in {"rain", "drizzle", "thunderstorm"}
        or "rain" in description
        or "drizzle" in description
        or "thunder" in description
    ):
        return WEATHER_RAIN
    if condition == "clear":
        return WEATHER_SUNNY
    if condition in {
        "clouds",
        "mist",
        "smoke",
        "haze",
        "dust",
        "fog",
        "sand",
        "ash",
        "squall",
        "tornado",
    }:
        return WEATHER_CLOUDY
    if any(token in description for token in ("cloud", "mist", "fog", "haze", "overcast")):
        return WEATHER_CLOUDY
    return WEATHER_CLOUDY


def _build_frame(mode: str, step: int) -> list[RGB]:
    if mode == WARNING_ONE_MINUTE:
        return _warning_one_minute_frame(step)
    if mode == WARNING_FIVE_MINUTE:
        return _warning_five_minute_frame(step)
    if mode == WEATHER_SUNNY:
        return _sunny_frame(step)
    if mode == WEATHER_RAIN:
        return _rain_frame(step)
    if mode == WEATHER_SNOW:
        return _snow_frame(step)
    return _cloudy_frame(step)


def _animation_cycle_length(mode: str) -> int:
    if mode == WARNING_ONE_MINUTE:
        return 4
    if mode in {WARNING_FIVE_MINUTE, WEATHER_SUNNY, WEATHER_CLOUDY}:
        return 8
    if mode == WEATHER_RAIN:
        return len(RAIN_STEPS)
    if mode == WEATHER_SNOW:
        return len(SNOW_STEPS)
    return 8


def _warning_five_minute_frame(step: int) -> list[RGB]:
    pulse = (12, 24, 48, 84, 120, 84, 48, 24)[step % 8]
    frame = [RGB(pulse, pulse // 2, 0) for _ in range(num_leds)]
    accent = min(pulse + 30, 160)
    for index in range(0, num_leds, 6):
        frame[index] = RGB(accent, accent // 2, 0)
    return frame


def _warning_one_minute_frame(step: int) -> list[RGB]:
    if step % 4 in {2, 3}:
        return blank_frame()

    frame = [RGB(140, 0, 0) for _ in range(num_leds)]
    for index in range(0, num_leds, 3):
        frame[index] = RGB(220, 24, 24)
    return frame


def _sunny_frame(step: int) -> list[RGB]:
    glow = (72, 82, 92, 102, 110, 102, 92, 82)[step % 8]
    frame = [RGB(glow, max(glow - 12, 0), 0) for _ in range(num_leds)]
    for index in range(0, num_leds, 9):
        frame[index] = RGB(min(glow + 25, 140), min(glow + 5, 120), 0)
    return frame


def _cloudy_frame(step: int) -> list[RGB]:
    glow = (38, 42, 46, 52, 58, 52, 46, 42)[step % 8]
    return [RGB(glow, glow, min(glow + 22, 96)) for _ in range(num_leds)]


def _rain_frame(step: int) -> list[RGB]:
    current = RAIN_STEPS[step % len(RAIN_STEPS)]
    trailing = RAIN_STEPS[(step - 1) % len(RAIN_STEPS)]
    frame = [RGB(0, 0, 10) for _ in range(num_leds)]
    for index in trailing:
        frame[index] = RGB(0, 0, 42)
    for index in current:
        frame[index] = RGB(0, 0, 120)
    return frame


def _snow_frame(step: int) -> list[RGB]:
    current = SNOW_STEPS[step % len(SNOW_STEPS)]
    trailing = SNOW_STEPS[(step - 1) % len(SNOW_STEPS)]
    frame = [RGB(4, 4, 10) for _ in range(num_leds)]
    for index in trailing:
        frame[index] = RGB(60, 60, 80)
    for index in current:
        frame[index] = RGB(120, 120, 140)
    return frame
