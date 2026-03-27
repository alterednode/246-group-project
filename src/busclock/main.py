from __future__ import annotations

import asyncio
import logging
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
    finally:
        LOGGER.info("Shutting down BusClock application")
        with suppress(Exception):
            await runner.cleanup()
        await runtime.stop()
