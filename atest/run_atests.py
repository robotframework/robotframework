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

import subprocess
import os.path
import shutil
import sys

CURDIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(CURDIR, '..', 'src'))

import robot


ARGUMENTS = ' '.join('''
--doc RobotSPFrameworkSPacceptanceSPtests
--reporttitle RobotSPFrameworkSPTestSPReport
--logtitle RobotSPFrameworkSPTestSPLog
--metadata interpreter:%(INTERPRETER)s
--metadata platform:%(PLATFORM)s
--variable interpreter:%(INTERPRETER)s
--pythonpath %(PYTHONPATH)s
--include %(RUNNER)s
--outputdir %(OUTPUTDIR)s
--output output.xml
--report report.html
--log log.html
--escape space:SP
--escape star:STAR
--escape paren1:PAR1
--escape paren2:PAR2
--critical regression
--SplitOutputs 2
--SuiteStatLevel 3
--TagStatCombine jybotNOTpybot
--TagStatCombine pybotNOTjybot
--TagStatExclude pybot
--TagStatExclude jybot
'''.strip().splitlines())


def main(interpreter, *params):
    resultdir = os.path.join(CURDIR, 'results')
    if os.path.isdir(resultdir):
        shutil.rmtree(resultdir)
    args = ARGUMENTS % {
        'PYTHONPATH' : os.path.join(CURDIR, 'resources'),
        'OUTPUTDIR' : resultdir,
        'INTERPRETER': interpreter,
        'PLATFORM': sys.platform,
        'RUNNER': ('pybot 'if 'python' in os.path.basename(interpreter)
                   else 'jybot')
        }
    runner = os.path.join(os.path.dirname(robot.__file__), 'runner.py')
    command = '%s %s %s %s' % (sys.executable, runner, args, ' '.join(params))
    print 'Running command\n%s\n' % command
    sys.stdout.flush()
    return subprocess.call(command.split())


if __name__ == '__main__':
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print __doc__
        rc = 251
    else:
        rc = main(*sys.argv[1:])
    sys.exit(rc) 
