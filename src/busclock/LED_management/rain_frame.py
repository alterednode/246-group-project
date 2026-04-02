from __future__ import annotations

from .RGB import RGB, blank_frame
from .base import FrameAnimation

RAIN_STEPS: tuple[tuple[int, ...], ...] = (
    (51, 99, 97, 93, 72, 65, 3, 7, 11, 18, 22, 30, 14),
    (19, 29, 32, 39, 26, 69,33),
    (42, 70, 67, 56, 49, 83, 59)
)


class RainAnimation(FrameAnimation):
    frame_duration_seconds = 0.2
    frame_count = len(RAIN_STEPS)

    def frame(self, step: int) -> list[RGB]:
        frame = blank_frame()
        for index in RAIN_STEPS[step % self.frame_count]:
            frame[index] = RGB(0, 0, 100)
        return frame
