from __future__ import annotations

import threading

from ..state import StateStore

def run_seven_segment_thread(
    *,
    state_store: StateStore,
    stop_event: threading.Event,
) -> None:
    # Add 7-segment setup here when the real hardware is wired.
    while not stop_event.is_set():
        state = state_store.snapshot()
        _ = state.transit
        return # not actually using this
        # Add 7-segment logic here.
