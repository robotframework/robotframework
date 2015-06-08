import time
from robot.api import logger


def log_with_all_levels():
    for level in 'trace debug info warn error'.split():
        msg = '%s msg' % level
        logger.write(msg+' 1', level)
        getattr(logger, level)(msg+' 2', html=False)


def write(message, level):
    logger.write(message, level)


def log_messages_different_time():
    logger.info('First message')
    time.sleep(0.1)
    logger.info('Second message 0.1 sec later')


def log_html():
    logger.write('<b>debug</b>', level='DEBUG', html=True)
    logger.info('<b>info</b>', html=True)
    logger.warn('<b>warn</b>', html=True)


def write_messages_to_console():
    logger.console('To console only')
    logger.console('To console ', newline=False)
    logger.console('in two parts')
    logger.info('To log and console', also_console=True)


def log_non_strings():
    logger.info(42)
    logger.warn(True)


def log_callable():
    logger.info(log_callable)
