import logging
import time

from robot.api import logger
from robot.output.pyloggingconf import RobotHandler

# Use simpler formatter to avoid flakeynes that started to occur after enhancing
# message formatting in https://github.com/robotframework/robotframework/pull/4147
# Without this change execution on PyPy failed about every third time so that
# timeout was somehow ignored. On CI the problem occurred also with Python 3.9.
# Not sure why the problem occurred, but it seems to be related to the logging
# module and not related to the bug that this library is testing. This hack ought
# to thus be safe.
for handler in logging.getLogger().handlers:
    if isinstance(handler, RobotHandler):
        handler.format = lambda record: record.getMessage()


MSG = "A rather long message that is slow to write on the disk. " * 10000


def rf_logger():
    _log_a_lot(logger.info)


def python_logger():
    _log_a_lot(logging.info)


# Binding global values to argument default values is a performance optimization
# to give as much time as possible for actual logging.
def _log_a_lot(info, msg=MSG, sleep=time.sleep, current=time.time):
    end = current() + 1
    while current() < end:
        info(msg)
        sleep(0)  # give time for other threads
    raise AssertionError("Execution should have been stopped by timeout.")
