import time

from robot.api import logger


def log_with_all_levels():
    for level in "trace debug info warn error".split():
        msg = f"{level} msg"
        logger.write(msg + " 1", level)
        getattr(logger, level)(msg + " 2", html=False)


def write(message, level):
    logger.write(message, level)


def log_messages_different_time():
    logger.info("First message")
    time.sleep(0.1)
    logger.info("Second message 0.1 sec later")


def log_html():
    logger.write("<b>debug</b>", level="DEBUG", html=True)
    logger.info("<b>info</b>", html=True)
    logger.warn("<b>warn</b>", html=True)


def write_messages_to_log_and_console():
    logger.console("To console only")
    logger.console("To console ", newline=False)
    logger.console("in two parts")
    logger.info("Info message to log and console w/ 'also_console'", also_console=True)
    logger.info("Info message to log and console w/ 'console'", also_console=True)
    # Warnings and errors are also logged to console by default
    logger.warn("Warn message to log and console")
    logger.error("Error message to log and console")
    # Info messages are only logged to log by default
    logger.info("Info message only to log")
    logger.warn("Warn message only to log", console=False)
    logger.error("Error message only to log", console=False)


def log_non_strings():
    logger.info(42)
    logger.warn(True, html=True)
    logger.info(None)


def log_callable():
    logger.info(log_callable)
