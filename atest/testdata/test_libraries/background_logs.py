import threading
from robot.api.logger import BackgroundLogger


logger = BackgroundLogger()


def log_from_main(msg):
    logger.info(msg)


def log_from_background(msg, thread=None):
    t = threading.Thread(target=logger.info, args=(msg,))
    if thread:
        t.setName(thread)
    t.start()


def log_background_messages(thread=None):
    logger.log_background_messages(thread)
