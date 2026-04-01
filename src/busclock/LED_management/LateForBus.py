from __future__ import annotations

from .RGB import RGB, blank_frame, num_leds, solid_frame
from .base import FrameAnimation


class SoonBusAnimation(FrameAnimation):
    frame_duration_seconds = 0.25
    frame_count = 8

    def frame(self, step: int) -> list[RGB]:
        pulse = (12, 24, 48, 84, 120, 84, 48, 24)[step % self.frame_count]
        frame = solid_frame(pulse, pulse // 2, 0)
        accent = min(pulse + 30, 160)
        for index in range(0, num_leds, 6):
            frame[index] = RGB(accent // 4, accent // 8, 0)
        return frame


class LateForBusAnimation(FrameAnimation):
    frame_duration_seconds = 0.5
    frame_count = 2

    def frame(self, step: int) -> list[RGB]:
        if step % self.frame_count == 1:
            return blank_frame()
        return solid_frame(100, 3, 3)
