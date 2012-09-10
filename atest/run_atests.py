#!/usr/bin/env python

"""A script for running Robot Framework's acceptance tests.

Usage:  run_atests.py interpreter [options] datasource(s)

Data sources are paths to directories or files under `robot` folder.

Available options are the same that can be used with Robot Framework.
See its help (e.g. `pybot --help`) for more information.

The specified interpreter is used by acceptance tests under `robot` to
run test cases under `testdata`. It can be simply `python` or `jython`
(if they are in PATH) or to a path a selected interpreter (e.g.
`/usr/bin/python26`). Note that this script itself must always be
executed with Python.

Examples:
$ atest/run_atests.py python --test example atest/robot
$ atest/run_atests.py /usr/bin/jython25 atest/robot/tags/tag_doc.txt
"""

import os
import signal
import subprocess
import sys
from os.path import abspath, basename, dirname, isdir, join, normpath
from shutil import rmtree

CURDIR = dirname(abspath(__file__))
RUNNER = normpath(join(CURDIR, '..', 'src', 'robot', 'run.py'))
RESULTS = join(CURDIR, 'results')
ARGUMENTS = ' '.join('''
--doc RobotSPFrameworkSPacceptanceSPtests
--reporttitle RobotSPFrameworkSPTestSPReport
--logtitle RobotSPFrameworkSPTestSPLog
--metadata Interpreter:%(INTERPRETER)s
--metadata Platform:%(PLATFORM)s
--variable INTERPRETER:%(INTERPRETER)s
--variable STANDALONE_JYTHON:NO
--pythonpath %(PYTHONPATH)s
--include %(INCLUDE)s
--outputdir %(OUTPUTDIR)s
--output output.xml
--report report.html
--log log.html
--splitlog
--escape space:SP
--escape star:STAR
--escape paren1:PAR1
--escape paren2:PAR2
--critical regression
--SuiteStatLevel 3
--TagStatCombine jybotNOTpybot
--TagStatCombine pybotNOTjybot
--TagStatExclude pybot
--TagStatExclude jybot
--TagStatExclude x-*
'''.strip().split())


def atests(interpreter, *params):
    if isdir(RESULTS):
        rmtree(RESULTS)
    args = ARGUMENTS % {
        'PYTHONPATH' : join(CURDIR, 'resources'),
        'OUTPUTDIR' : RESULTS,
        'INTERPRETER': interpreter,
        'PLATFORM': sys.platform,
        'INCLUDE': 'jybot' if 'jython' in basename(interpreter) else 'pybot'
    }
    if os.name == 'nt':
        args += ' --exclude nonwindows'
    if sys.platform == 'darwin' and 'python' in basename(interpreter):
        args += ' --exclude nonmacpython'
    command = '%s %s %s %s' % (sys.executable, RUNNER, args, ' '.join(params))
    print 'Running command\n%s\n' % command
    sys.stdout.flush()
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    return subprocess.call(command.split())


if __name__ == '__main__':
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print __doc__
        rc = 251
    else:
        rc = atests(*sys.argv[1:])
    sys.exit(rc)
