#!/usr/bin/env python

"""Usage: check_test_times.py seconds inpath [outpath]

Reads result of a test run from Robot output file and checks that no test
took longer than given amount of seconds to execute. If outpath is not
given, the result is written over the original file.
"""

import sys
from robot.api import ExecutionResult, ResultVisitor


class ExecutionTimeChecker(ResultVisitor):

    def __init__(self, max_seconds):
        self.max_milliseconds = max_seconds * 1000

    def visit_test(self, test):
        if test.status == 'PASS' and test.elapsedtime > self.max_milliseconds:
            test.status = 'FAIL'
            test.message = 'Test execution took too long.'


def check_tests(max_seconds, inpath, outpath=None):
    if not outpath:
        outpath = inpath
    result = ExecutionResult(inpath)
    result.suite.visit(ExecutionTimeChecker(int(max_seconds)))
    result.save(outpath)

if __name__ == '__main__':
    try:
        check_tests(*sys.argv[1:])
    except TypeError:
        print __doc__
