import threading
import logging
import time

from robot.api import logger



def log_using_robot_api_in_thread():
    threading.Timer(0.1, log_using_robot_api, kwargs={"in_thread": True}).start()

def log_using_robot_api(in_thread=False):
    for i in range(100):
        if in_thread:
            logger.warn(
                ("In thread {0}: {1}\n" * 100).format(
                    threading.currentThread().getName(), str(i)
                )
            )
        else:
            logger.info(str(i))
        time.sleep(0.01)

def log_using_logging_module_in_thread():
    threading.Timer(0.1, log_using_logging_module, kwargs={"in_thread": True}).start()

def log_using_logging_module(in_thread=False):
    for i in range(100):
        if in_thread:
            logging.warning(
                ("In thread {0}: {1}\n" * 100).format(
                    threading.currentThread().getName(), str(i)
                )
            )
        else:
            logging.info(str(i))
        time.sleep(0.01)
