import logging
import sys

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logger(name, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
