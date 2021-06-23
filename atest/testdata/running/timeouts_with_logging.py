import logging
import time

from robot.api import logger


MSG = 'A rather long message that is slow to write on the disk. ' * 10000


def rf_logger():
    _log_a_lot(logger.info)


def python_logger():
    _log_a_lot(logging.info)


def _log_a_lot(info):
    # Assigning local variables is performance optimization to give as much
    # time as as possible for actual logging.
    msg = MSG
    sleep = time.sleep
    current = time.time
    end = current() + 1
    while current() < end:
        info(msg)
        sleep(0)    # give time for other threads
    raise AssertionError('Execution should have been stopped by timeout.')
