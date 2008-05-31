import sys
import os

from robot.parsing import TestSuite

from apihelper import verify_suites, verify_tests


BASE = os.path.dirname(os.path.abspath(sys.argv[0]))
DATA = os.path.join(BASE, 'testdata')                    

def parse_suite(path):
    suite = TestSuite(path)
    fails = verify_suites(suite, os.path.join(DATA, 'parsing_suite_data.txt'))
    fails += verify_tests(suite, os.path.join(DATA, 'parsing_test_data.txt'))
                  
    print 'Total failures: %d' % fails 
    return fails

   
if __name__ == '__main__':
    sys.exit(parse_suite(DATA))
