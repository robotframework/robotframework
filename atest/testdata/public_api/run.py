import os
import sys

from robot import run

from apihelper import verify_suites, verify_tests, remove_outputdir

BASE = os.path.dirname(os.path.abspath(sys.argv[0]))
DATA = os.path.join(BASE, 'testdata')
OUTPUT = os.path.join(BASE, 'output')


def run_suite():
    suite = run(DATA, outputdir=OUTPUT, monitorcolors='off')
    fails = verify_suites(suite, os.path.join(DATA, 'run_suite_data.txt'))
    fails += verify_tests(suite, os.path.join(DATA,'run_test_data.txt'))
                    
    print 'Total failures: %d' % fails 
    remove_outputdir()
    return fails

    

if __name__ == '__main__':
    sys.exit(run_suite())
