import logging
import time

from robot.api import logger


MSG = 'A rather long message that is slow to write on the disk. ' * 10000


def rf_logger():
    while True:
        logger.info(MSG)
        time.sleep(0)    # give time for other threads


def python_logging():
    while True:
        logging.info(MSG)
        time.sleep(0)    # give time for other threads
