from __future__ import annotations

import sys

from .LateForBus import LateForBusAnimation, SoonBusAnimation
from .RGB import blank_frame
from .cloudy_frame import CloudyAnimation
from .rain_frame import RainAnimation
from .snowing import SnowAnimation
from .sunny import SunnyAnimation

ANIMATION_NAMES = ("snowing", "raining", "sunny", "late", "soon", "cloudy", "off")
TEST_ANIMATION = "sunny"
TEST_FRAMES: int | None = None
TEST_DURATION_SECONDS: float | None = 10.0


def animation_for_name(name: str):
    normalized = name.strip().casefold()
    if normalized == "snowing":
        return SnowAnimation()
    if normalized == "raining":
        return RainAnimation()
    if normalized == "sunny":
        return SunnyAnimation()
    if normalized == "late":
        return LateForBusAnimation()
    if normalized == "soon":
        return SoonBusAnimation()
    if normalized == "cloudy":
        return CloudyAnimation()
    if normalized == "off":
        return None
    raise ValueError(f"Unknown LED animation '{name}'.")


def led(weather: str, controller, *, frames: int | None = None, duration_seconds: float | None = None) -> None:
    animation = animation_for_name(weather)
    if animation is None:
        controller.display(blank_frame())
        return
    animation.play(
        controller,
        frames=frames,
        duration_seconds=duration_seconds,
    )

# PYTHONPATH=src python3 -m busclock.LED_management.test
# Commant to run this I think
def main() -> int:
    try:
        from ..electronics.LEDs import LEDControl
    except Exception as exc:
        print(f"Unable to initialize LED controller: {exc}", file=sys.stderr)
        return 1

    if TEST_ANIMATION not in ANIMATION_NAMES:
        print(
            f"Unknown TEST_ANIMATION {TEST_ANIMATION!r}. Choose from: {', '.join(ANIMATION_NAMES)}",
            file=sys.stderr,
        )
        return 1

    controller = LEDControl()
    led(
        TEST_ANIMATION,
        controller,
        frames=TEST_FRAMES,
        duration_seconds=TEST_DURATION_SECONDS,
    )
    controller.display(blank_frame())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
