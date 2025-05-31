# backend/utils/logger.py

import logging
from rich.logging import RichHandler


def setup_logger(name="courtroom", level=logging.INFO):
    """
    Set up a structured logger with Rich formatting.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)
        handler = RichHandler(rich_tracebacks=True)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger