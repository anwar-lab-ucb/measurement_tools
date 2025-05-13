import logging
import sys


def create_logger(name=None, fname=None, quiet=False, level=logging.DEBUG):
    """If `fname` is None, just prints to stdout"""
    if name == None:
        name = __name__
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(levelname)-8s %(name)s:%(filename)s:%(lineno)d (@ %(asctime)s) %(message)s"
    )

    if fname:
        file_handler = logging.FileHandler(fname, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if not quiet:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
