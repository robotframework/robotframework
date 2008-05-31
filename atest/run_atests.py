#!/usr/bin/env python

"""A script for running Robot Framework's acceptance tests.

Usage:  run_atests.py interpreter [options] datasource(s)

Data sources are paths to directories or files under 'robot' folder.

Available options are the same that can be used with Robot Framework.
See its help (e.g. 'pybot --help') for more information.

The specified interpreter is used by acceptance tests under 'robot' to
run test cases under 'testdata'. It can be simply 'python' or 'jython'
(if they are in PATH) or to a path a selected interpreter (e.g.
'/usr/bin/python23'). Note that this script itself must always be
executed with Python.

Examples:
$ atest/run_atests.py python --splitoutputs 2 atest/robot
$ atest/run_atests.py /usr/bin/jython22 atest/robot/core/variables.html
"""

import os
import sys

import robot


ACCDIR = os.path.join(os.path.abspath(os.path.dirname(__file__)))

DEFAULT_ARGS = '''
--doc RobotSPacceptanceSPtestsSPonSP%(pj)sython
--metadata interpreter:%(interpreter)s
--variable interpreter:%(interpreter)s
--pythonpath %(pythonpath)s
--include %(pj)sybot
--outputdir %(outdir)s
--output %(pj)sybot-output.xml
--report %(pj)sybot-report.html
--log %(pj)sybot-log.html
--escape space:SP
--escape star:STAR
--escape paren1:PAR1
--escape paren2:PAR2
--critical regression
--critical smoke
--SplitOutputs 2
--SuiteStatLevel 3
--TagStatCombine jybotNOTpybot
--TagStatCombine pybotNOTjybot
--TagStatLink jybot:http://jython.org:Jython
--TagStatLink pybot:http://python.org:Python
--TagStatLink jybot-bug-STAR:http://bugs.jython.org/issue%%1:Tracker
'''.strip().splitlines()

ARG_VALUES = { 'pythonpath' : os.path.join(ACCDIR,'resources'),
               'outdir' : os.path.join(ACCDIR,'results'),
             }

def main(interpreter, *params):
    ARG_VALUES['interpreter'] = interpreter
    ARG_VALUES['pj'] = 'python' in os.path.basename(interpreter) and 'p' or 'j'
    runner = os.path.join(os.path.dirname(robot.__file__), 'runner.py')
    command = '%s %s %s %s' % (sys.executable, runner,
                               ' '.join(DEFAULT_ARGS) % ARG_VALUES,
                               ' '.join(params))
    print "Running command\n%s\n" % command
    sys.stdout.flush()
    rc = os.system(command)
    sys.exit(rc)


if __name__ == '__main__':
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print __doc__
        sys.exit(1) 
    main(*sys.argv[1:])
