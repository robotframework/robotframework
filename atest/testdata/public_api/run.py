import os

from robot import run

from apihelper import verify_suites, verify_tests


def run_suite(base):
    suite = run(os.path.join(base, 'testdata'), outputdir=os.path.join(base, 'output'))
    fails = verify_suites(suite, os.path.join(base, 'testdata', 'run_suite_data.txt'))
    fails += verify_tests(suite, os.path.join(base, 'testdata', 'run_test_data.txt'))
                    
    print 'Total failures: %d' % fails 
 #   _remove_outputdir('output')
    return fails
    

def _remove_outputdir(path):
    for file in os.listdir(path):
        print 'removing', file
        os.remove(file)
    os.remove(path)
    

if __name__ == '__main__':
    import sys
    base = os.path.dirname(os.path.abspath(sys.argv[0]))
    sys.exit(run_suite(base))
