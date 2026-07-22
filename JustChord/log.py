"""Centralized logging setup for JustChord."""

import logging

LOG_LEVEL = logging.DEBUG


def setup():
    """Configure the root justchord logger. Call once at app startup."""
    logger = logging.getLogger("justchord")
    if logger.handlers:
        return
    logger.setLevel(LOG_LEVEL)
    try:
        from rich.logging import RichHandler

        handler = RichHandler(rich_tracebacks=True, show_path=False, markup=False)
        handler.setFormatter(logging.Formatter("%(message)s"))
    except ImportError:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s.%(msecs)03d [%(name)s] %(message)s", datefmt="%H:%M:%S")
        )
    logger.addHandler(handler)
