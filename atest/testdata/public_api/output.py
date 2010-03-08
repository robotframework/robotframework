import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
from robot.output import TestSuite

from apihelper import verify_suites, verify_tests, remove_outputdir


BASE = os.path.dirname(os.path.abspath(sys.argv[0]))
DATA = os.path.join(BASE, 'testdata')

def read_and_modify_suite(path):
    suite = TestSuite(path)
    fails = verify_suites(suite, os.path.join(DATA, 'output_suite_data.txt'))
    fails += verify_tests(suite, os.path.join(DATA, 'output_test_data.txt'))

    _process_suite(suite)
    suite.set_status()
    fails = verify_suites(suite, os.path.join(DATA, 'output_modified_suite_data.txt'))
    fails += verify_tests(suite, os.path.join(DATA, 'output_modified_test_data.txt'))

    print 'Total failures: %d' % fails
    remove_outputdir()
    return fails

def _process_suite(suite):
    if suite.suites:
        for sub in suite.suites:
            if sub.status == 'FAIL':
                sub.status = 'PASS'
            _process_suite(sub)
    if not suite.tests:
        return
    for test in suite.tests:
        if test.status == 'FAIL':
            test.status = 'PASS'
        if not test.keywords:
            return
        for kw in test.keywords:
            if kw.status == 'FAIL':
                kw.status = 'PASS'


if __name__ == '__main__':
    import robot
    robot.run(DATA, outputdir=os.path.join(BASE,'output'))
    sys.exit(read_and_modify_suite(os.path.join(BASE,'output','output.xml')))
