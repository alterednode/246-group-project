from __future__ import annotations

from .RGB import RGB, solid_frame
from .base import FrameAnimation


class SunnyAnimation(FrameAnimation):
    frame_duration_seconds = 0.5
    frame_count = 1

    def frame(self, step: int) -> list[RGB]:
        _ = step
        return solid_frame(100, 100, 0)
