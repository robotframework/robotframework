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

import signal
import subprocess
import os.path
import shutil
import glob
import sys
from zipfile import ZipFile, ZIP_DEFLATED

CURDIR = os.path.dirname(os.path.abspath(__file__))
RESULTDIR = os.path.join(CURDIR, 'results')

sys.path.insert(0, os.path.join(CURDIR, '..', 'src'))

import robot


ARGUMENTS = ' '.join('''
--doc RobotSPFrameworkSPacceptanceSPtests
--reporttitle RobotSPFrameworkSPTestSPReport
--logtitle RobotSPFrameworkSPTestSPLog
--metadata Interpreter:%(INTERPRETER)s
--metadata Platform:%(PLATFORM)s
--variable INTERPRETER:%(INTERPRETER)s
--variable STANDALONE_JYTHON:NO
--pythonpath %(PYTHONPATH)s
--include %(RUNNER)s
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
'''.strip().splitlines())


def atests(interpreter, *params):
    if os.path.isdir(RESULTDIR):
        shutil.rmtree(RESULTDIR)
    runner = ('jython' in os.path.basename(interpreter) and 'jybot'
                   or 'pybot')
    args = ARGUMENTS % {
        'PYTHONPATH' : os.path.join(CURDIR, 'resources'),
        'OUTPUTDIR' : RESULTDIR,
        'INTERPRETER': interpreter,
        'PLATFORM': sys.platform,
        'RUNNER': runner
        }
    if os.name == 'nt':
        args += ' --exclude nonwindows'
    if sys.platform == 'darwin' and runner == 'pybot':
        args += ' --exclude nonmacpython'
    runner = os.path.join(os.path.dirname(robot.__file__), 'run.py')
    command = '%s %s %s %s' % (sys.executable, runner, args, ' '.join(params))
    print 'Running command\n%s\n' % command
    sys.stdout.flush()
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    return subprocess.call(command.split())


def buildbot(interpreter, *params):
    params = '--log NONE --report NONE --SplitOutputs 1'.split() + list(params)
    rc = atests(interpreter, *params)
    zippath = os.path.join(RESULTDIR, 'outputs.zip')
    zipfile = ZipFile(zippath, 'w', compression=ZIP_DEFLATED)
    for output in glob.glob(os.path.join(RESULTDIR, '*.xml')):
        zipfile.write(output, os.path.basename(output))
    zipfile.close()
    print 'Archive:', zippath
    return rc


if __name__ == '__main__':
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print __doc__
        rc = 251
    elif sys.argv[1] == 'buildbot':
        rc = buildbot(*sys.argv[2:])
    else:
        rc = atests(*sys.argv[1:])
    sys.exit(rc)
