from __future__ import print_function
import sys
import os

from robot.api import SuiteVisitor


ROBOT_LISTENER_API_VERSION = 3


def startTest(data, result):
    result.message = '[Start] [data] ' + data.name + ' [result] ' + result.name
#    data.name = data.doc = result.name = 'Not visible in results'
#    result.doc = (result.doc + ' [start test]').strip()
#    result.tags.add('[start]')
#    result.message = 'Message: [start]'
#    result.parent.metadata['tests'] += 'x'
#    data.name = data.doc = 'Not visible in results'
#    data.keywords.create('No Operation')


def end_test(data, result): 
    result.message += ' [END] [data] ' + data.name + ' [result] ' + result.name
#    result.name = 'Does not go to output.xml'
#    result.doc += ' [end test]'
#    result.tags.add('[end]')
#    result.passed = not result.passed
#    result.message += ' [end]'
#    data.name = data.doc = 'Not visible in results'
#
