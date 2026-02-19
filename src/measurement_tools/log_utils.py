import logging
import sys
from pathlib import Path


def create_logger(name=None, fname=None, quiet=False, level=logging.DEBUG):
    """Configure a logger with standardized formatting.

    If `name` is None, configures the root logger (useful for application
    entry points - child loggers will inherit handlers).
    If `fname` is None, just prints to stdout.
    If `quiet` is True, suppresses stdout output.
    """
    logger = logging.getLogger(name)

    # a logger of this name might have previously been registered
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(levelname)-8s %(name)s:%(filename)s:%(lineno)d (@ %(asctime)s) %(message)s"
    )

    if fname:
        Path(fname).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(fname, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if not quiet:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
