import os
import time


class MyException(Exception):
    pass


def passing(*args):
    pass


def sleeping(seconds=1):
    orig = seconds
    while seconds > 0:
        time.sleep(min(seconds, 0.1))
        seconds -= 0.1
    os.environ["ROBOT_THREAD_TESTING"] = str(orig)
    return orig


def returning(arg):
    return arg


def failing(msg="xxx"):
    raise MyException(msg)
