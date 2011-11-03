import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
from robot import run

from apihelper import verify_suites, verify_tests, remove_outputdir

BASE = os.path.dirname(os.path.abspath(sys.argv[0]))
DATA = os.path.join(BASE, 'testdata')
OUTPUT = os.path.join(BASE, 'output')


def run_suite():
    suite, _ = run(DATA, outputdir=OUTPUT, monitorcolors='off')
    fails = verify_suites(suite, os.path.join(DATA, 'run_suite_data.txt'))
    fails += verify_tests(suite, os.path.join(DATA,'run_test_data.txt'))

    print 'Total failures: %d' % fails
    remove_outputdir()
    return fails


if __name__ == '__main__':
    sys.exit(run_suite())
