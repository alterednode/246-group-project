from __future__ import annotations

import threading
import time
from typing import Protocol

from .RGB import RGB


class LEDDisplay(Protocol):
    def display(self, frame: list[RGB]) -> None:
        ...


class FrameAnimation:
    frame_duration_seconds = 0.25
    frame_count = 1

    def frame(self, step: int) -> list[RGB]:
        raise NotImplementedError

    def frame_at(self, step: int) -> list[RGB]:
        return self.frame(step % self.frame_count)

    def play(
        self,
        controller: LEDDisplay,
        *,
        frames: int | None = None,
        duration_seconds: float | None = None,
        stop_event: threading.Event | None = None,
    ) -> int:
        if frames is None and duration_seconds is None:
            frames = self.frame_count

        deadline = None if duration_seconds is None else time.monotonic() + duration_seconds
        step = 0
        played_frames = 0

        while True:
            if stop_event is not None and stop_event.is_set():
                break
            if frames is not None and played_frames >= frames:
                break
            if deadline is not None and time.monotonic() >= deadline:
                break

            controller.display(self.frame_at(step))
            played_frames += 1
            step += 1

            if stop_event is None:
                time.sleep(self.frame_duration_seconds)
            elif stop_event.wait(self.frame_duration_seconds):
                break

        return played_frames
