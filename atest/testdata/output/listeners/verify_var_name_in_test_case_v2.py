import logging
from robot.api import logger

ROBOT_LISTENER_API_VERSION = 2


def startTest(name, info):
    print('[Start] [name] ' + name)

def end_test(name, info):
    print('[END] [name] ' + name)