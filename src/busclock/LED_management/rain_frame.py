from __future__ import annotations

from .RGB import RGB, blank_frame
from .base import FrameAnimation

RAIN_STEPS: tuple[tuple[int, ...], ...] = (
    (3, 7, 11, 18, 22, 30),
    (19, 27, 29, 40, 54, 69),
    (42, 49, 55, 71, 83, 95),
    (3, 7, 11, 51, 73, 81, 94, 98),
)


class RainAnimation(FrameAnimation):
    frame_duration_seconds = 0.2
    frame_count = len(RAIN_STEPS)

    def frame(self, step: int) -> list[RGB]:
        frame = blank_frame()
        for index in RAIN_STEPS[step % self.frame_count]:
            frame[index] = RGB(0, 0, 100)
        return frame
