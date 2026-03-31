from __future__ import annotations

import asyncio
import logging
import signal
from contextlib import suppress

from aiohttp import web

from .env import load_env_file
from .logging_utils import configure_logging
from .runtime import BusClockRuntime
from .web import create_web_app

LOGGER = logging.getLogger(__name__)


async def main() -> None:
    load_env_file()
    configure_logging()
    LOGGER.info("Starting BusClock application")

    runtime = BusClockRuntime()

    # Register signal handlers so a SIGINT/SIGTERM will set the hardware
    # stop event immediately and allow threads to exit cleanly.
    loop = asyncio.get_running_loop()
    try:
        loop.add_signal_handler(signal.SIGINT, runtime._hardware_stop_event.set)
        loop.add_signal_handler(signal.SIGTERM, runtime._hardware_stop_event.set)
    except NotImplementedError:
        # Fall back to the basic signal handlers which receive (signum, frame)
        signal.signal(signal.SIGINT, lambda s, f: runtime._hardware_stop_event.set())
        signal.signal(signal.SIGTERM, lambda s, f: runtime._hardware_stop_event.set())

    await runtime.start()

    app = create_web_app(runtime)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        host=runtime.settings.host,
        port=runtime.settings.port,
    )
    await site.start()
    LOGGER.info(
        "BusClock web server listening on %s:%s",
        runtime.settings.host,
        runtime.settings.port,
    )

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        LOGGER.info("Keyboard interrupt received, stopping hardware threads")
        # Ensure stop event is set in case the signal handler didn't run.
        runtime._hardware_stop_event.set()
        raise
    finally:
        LOGGER.info("Shutting down BusClock application")
        with suppress(Exception):
            await runner.cleanup()
        await runtime.stop()
