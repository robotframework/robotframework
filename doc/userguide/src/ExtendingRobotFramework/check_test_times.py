#!/usr/bin/env python

"""Usage: check_test_times.py inpath [outpath]

Reads result of a test run from Robot output file and checks that no test 
took longer than 3 minutest to execute. If outpath is not given, the
result is written over the original file.
"""

import sys
from robot.output import TestSuite


def check_tests(inpath, outpath=None):
    if not outpath:
        outpath = inpath
    suite = TestSuite(inpath)
    _check_execution_times(suite)
    suite.write_to_file(outpath)

def _check_execution_times(suite):
    for test in suite.tests:
        if test.status == 'PASS' and test.elapsedtime > 1000 * 60 * 3:
            test.status = 'FAIL'
            test.message = 'Test execution time was too long: %s' % test.elapsedtime
    for suite in suite.suites:
        _check_execution_times(suite)


if __name__ == '__main__':
    try:
        check_tests(*sys.argv[1:])
    except TypeError:
        print __doc__
