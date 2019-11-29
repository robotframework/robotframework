from __future__ import print_function
import sys
import os

from robot.api import SuiteVisitor


ROBOT_LISTENER_API_VERSION = 3


def startTest(data, result):
    result.message = '[Start] [data] ' + data.name + ' [result] ' + result.name

def end_test(data, result):
    result.message += ' [END] [data] ' + data.name + ' [result] ' + result.name
