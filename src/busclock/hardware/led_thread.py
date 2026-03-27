from __future__ import annotations

import threading

from ..state import StateStore

def run_led_thread(
    *,
    state_store: StateStore,
    stop_event: threading.Event,
) -> None:
    # Add LED setup here when the real hardware is wired.
    while not stop_event.is_set():
        state = state_store.snapshot()
        _ = state.transit
        _ = state.hardware.led_display
        # Add LED logic here.
