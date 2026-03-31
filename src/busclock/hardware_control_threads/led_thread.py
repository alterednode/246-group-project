from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ..LED_management.LateForBus import LateForBusAnimation, SoonBusAnimation
from ..LED_management.RGB import blank_frame
from ..LED_management.base import FrameAnimation
from ..LED_management.cloudy_frame import CloudyAnimation
from ..LED_management.rain_frame import RainAnimation
from ..LED_management.snowing import SnowAnimation
from ..LED_management.sunny import SunnyAnimation
from ..state import StateStore, SystemState, WeatherSnapshot

LOGGER = logging.getLogger(__name__)

FIVE_MINUTE_WARNING_SECONDS = 5 * 60
ONE_MINUTE_WARNING_SECONDS = 60

WARNING_FIVE_MINUTE = "warning_five_minutes"
WARNING_ONE_MINUTE = "warning_one_minute"
WEATHER_SUNNY = "weather_sunny"
WEATHER_CLOUDY = "weather_cloudy"
WEATHER_RAIN = "weather_rain"
WEATHER_SNOW = "weather_snow"


@dataclass(frozen=True, slots=True)
class AnimationSelection:
    mode: str
    reason: str


def run_led_thread(
    *,
    state_store: StateStore,
    stop_event: threading.Event,
) -> None:
    LOGGER.debug("LED thread starting")
    controller = _create_led_controller()
    animations = _animation_registry()
    active_selection: AnimationSelection | None = None
    step = 0

    try:
        while not stop_event.is_set():
            state = state_store.snapshot()
            selection = _select_animation(state)
            animation = animations[selection.mode]
            if selection != active_selection:
                LOGGER.info(
                    "LED animation changed to %s (%s, frame_count=%s, frame_duration=%ss)",
                    selection.mode,
                    selection.reason,
                    animation.frame_count,
                    animation.frame_duration_seconds,
                )
                active_selection = selection
                step = 0

            if controller is not None:
                controller.display(animation.frame_at(step))

            step = (step + 1) % animation.frame_count
            stop_event.wait(animation.frame_duration_seconds)
    finally:
        LOGGER.debug("LED thread stopping")
        if controller is not None:
            controller.display(blank_frame())


def _animation_registry() -> dict[str, FrameAnimation]:
    return {
        WARNING_FIVE_MINUTE: SoonBusAnimation(),
        WARNING_ONE_MINUTE: LateForBusAnimation(),
        WEATHER_SUNNY: SunnyAnimation(),
        WEATHER_CLOUDY: CloudyAnimation(),
        WEATHER_RAIN: RainAnimation(),
        WEATHER_SNOW: SnowAnimation(),
    }


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

    return WEATHER_RAIN
# 
#    if weather.snow_1h_mm or weather.snow_3h_mm or condition == "snow" or "snow" in description:
#        return WEATHER_SNOW
#    if (
#        weather.rain_1h_mm
#        or weather.rain_3h_mm
#        or condition in {"rain", "drizzle", "thunderstorm"}
#        or "rain" in description
#        or "drizzle" in description
#        or "thunder" in description
#    ):
#        return WEATHER_RAIN
#    if condition == "clear":
#        return WEATHER_SUNNY
#    if condition in {
#        "clouds",
#        "mist",
#        "smoke",
#        "haze",
#        "dust",
#        "fog",
#        "sand",
#        "ash",
#        "squall",
#        "tornado",
#    }:
#        return WEATHER_CLOUDY
#    if any(token in description for token in ("cloud", "mist", "fog", "haze", "overcast")):
#        return WEATHER_CLOUDY
#    return WEATHER_CLOUDY
