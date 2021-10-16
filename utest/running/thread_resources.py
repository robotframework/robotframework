import os
import time


class MyException(Exception):
    pass


def passing(*args):
    pass


def sleeping(s):
    seconds = s
    while seconds > 0:
        time.sleep(min(seconds, 0.1))
        seconds -= 0.1
    os.environ['ROBOT_THREAD_TESTING'] = str(s)
    return s


def returning(arg):
    return arg


def failing(msg='xxx'):
    raise MyException(msg)
