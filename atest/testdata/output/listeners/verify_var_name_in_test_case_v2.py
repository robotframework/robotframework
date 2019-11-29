import logging
from robot.api import logger

ROBOT_LISTENER_API_VERSION = 2


def startTest(name, info):
    print('[Start] [name] ' + name + ' [resolved name] ' + info['resolved_name'])

def end_test(name, info):
    print('[END] [name] ' + name + ' [resolved name] ' + info['resolved_name'])