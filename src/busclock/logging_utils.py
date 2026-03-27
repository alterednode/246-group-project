from __future__ import annotations

import logging
import os

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = (
    "%(asctime)s %(levelname)s [%(name)s] %(message)s"
)


def configure_logging(level: str | None = None) -> None:
    resolved_level = (level or os.getenv("BUSCLOCK_LOG_LEVEL", DEFAULT_LOG_LEVEL)).upper()
    logging.basicConfig(
        level=getattr(logging, resolved_level, logging.INFO),
        format=DEFAULT_LOG_FORMAT,
    )
