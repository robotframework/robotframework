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
executed with Python 2.6 or newer.

Examples:
$ atest/run_atests.py python --test example atest/robot
$ atest/run_atests.py /usr/bin/jython25 atest/robot/tags/tag_doc.txt
"""

import os
import shutil
import signal
import subprocess
import sys
import tempfile
from os.path import abspath, basename, dirname, exists, join, normpath, splitext

if sys.version_info < (2, 6):
    sys.exit('Running this script requires Python 2.6 or newer.')

CURDIR = dirname(abspath(__file__))
RUNNER = normpath(join(CURDIR, '..', 'src', 'robot', 'run.py'))
ARGUMENTS = ' '.join('''
--console dotted
--doc RobotSPFrameworkSPacceptanceSPtests
--reporttitle RobotSPFrameworkSPTestSPReport
--logtitle RobotSPFrameworkSPTestSPLog
--metadata Interpreter:%(INTERPRETER)s
--metadata Platform:%(PLATFORM)s
--variable INTERPRETER:%(INTERPRETER)s
--variable PYTHON:%(PYTHON)s
--variable JYTHON:%(JYTHON)s
--variable IRONPYTHON:%(IRONPYTHON)s
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
--noncritical not_ready
--SuiteStatLevel 3
--TagStatCombine jybotNOTpybot
--TagStatCombine pybotNOTjybot
--TagStatExclude pybot
--TagStatExclude jybot
--TagStatExclude x-*
'''.strip().split())


def atests(interpreter_path, *params):
    interpreter = _get_interpreter_basename(interpreter_path)
    resultdir, tempdir = _get_result_and_temp_dirs(interpreter)
    args = ARGUMENTS % {
        'PYTHONPATH' : join(CURDIR, 'resources'),
        'OUTPUTDIR' : resultdir,
        'INTERPRETER': interpreter_path,
        'PYTHON': interpreter_path if 'python' in interpreter else '',
        'JYTHON': interpreter_path if 'jython' in interpreter else '',
        'IRONPYTHON': interpreter_path if 'ipy' in interpreter else '',
        'PLATFORM': sys.platform,
        'INCLUDE': 'jybot' if 'jython' in interpreter else 'pybot'
    }
    if os.name == 'nt':
        args += ' --exclude x-exclude-on-windows'
    if sys.platform == 'darwin' and 'python' in interpreter:
        args += ' --exclude x-exclude-on-osx-python'
    if 'ipy' in interpreter:
        args += ' --noncritical x-fails-on-ipy'
    command = '%s %s %s %s' % (sys.executable, RUNNER, args, ' '.join(params))
    environ = dict(os.environ, TEMPDIR=tempdir)
    print 'Running command\n%s\n' % command
    sys.stdout.flush()
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    return subprocess.call(command.split(), env=environ)

def _get_interpreter_basename(interpreter):
    interpreter = basename(interpreter)
    base, ext  = splitext(interpreter)
    if ext.lower() in ('.sh', '.bat', '.cmd', '.exe'):
        return base
    return interpreter

def _get_result_and_temp_dirs(interpreter):
    resultdir = join(CURDIR, 'results', interpreter)
    tempdir = join(tempfile.gettempdir(), 'robottests', interpreter)
    if exists(resultdir):
        shutil.rmtree(resultdir)
    if exists(tempdir):
        shutil.rmtree(tempdir)
    os.makedirs(tempdir)
    return resultdir, tempdir


if __name__ == '__main__':
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print __doc__
        rc = 251
    else:
        rc = atests(*sys.argv[1:])
    sys.exit(rc)
