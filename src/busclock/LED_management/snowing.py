from __future__ import annotations

from .RGB import RGB, blank_frame
from .base import FrameAnimation

SNOW_STEPS: tuple[tuple[int, ...], ...] = (
    (2, 6, 11, 18, 22, 25, 29),
    (20, 28, 38, 40, 44, 46, 69),
    (42, 53, 55, 65, 73, 75, 81),
    (50, 76, 79, 87, 94, 99),
)


class SnowAnimation(FrameAnimation):
    frame_duration_seconds = 0.5
    frame_count = len(SNOW_STEPS)

    def frame(self, step: int) -> list[RGB]:
        frame = blank_frame()
        for index in SNOW_STEPS[step % self.frame_count]:
            frame[index] = RGB(100, 100, 100)
        return frame
