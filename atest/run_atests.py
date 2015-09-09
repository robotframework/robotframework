#!/usr/bin/env python

"""A script for running Robot Framework's acceptance tests.

Usage:  run_atests.py interpreter [options] datasource(s)

Data sources are paths to directories or files under `robot` folder.

Available options are the same that can be used with Robot Framework.
See its help (e.g. `pybot --help`) for more information.

The specified interpreter is used by acceptance tests under `robot` to
run test cases under `testdata`. It can be simply `python` or `jython`
(if they are in PATH) or a path to a selected interpreter (e.g.
`/usr/bin/python26`) or a path to a robotframework standalone jar (e.g.
/tmp/robotframework-2.9dev234.jar).

As a special case the interpreter value `standalone` will compile a new
standalone jar from the current sources and execute the acceptance tests with
it.

Note that this script itself must always be executed with Python 2.6 or newer.

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


CURDIR = dirname(abspath(__file__))
SRC = join(CURDIR, '..', 'src', 'robot')
RUNNER = normpath(join(SRC, 'run.py'))
REBOT = normpath(join(SRC, 'rebot.py'))
TESTDOC = normpath(join(SRC, 'testdoc.py'))
LIBDOC = normpath(join(SRC, 'libdoc.py'))
TIDY = normpath(join(SRC, 'tidy.py'))


sys.path.append(join(CURDIR, '..'))
try:
    from tasks import jar
except ImportError:
    def jar(*args, **kwargs):
        raise RuntimeError("Craeting jar distribution requires 'invoke'.")


ARGUMENTS = '''
--doc RobotSPFrameworkSPacceptanceSPtests
--reporttitle RobotSPFrameworkSPTestSPReport
--logtitle RobotSPFrameworkSPTestSPLog
--metadata Interpreter:%(INTERPRETER)s
--metadata Platform:%(PLATFORM)s
--variable INTERPRETER:%(INTERPRETER)s
--variable PYTHON:%(PYTHON)s
--variable JYTHON:%(JYTHON)s
--variable IRONPYTHON:%(IRONPYTHON)s
--variable ROBOT:%(ROBOT)s
--variable REBOT:%(REBOT)s
--variable LIBDOC:%(LIBDOC)s
--variable TESTDOC:%(TESTDOC)s
--variable TIDY:%(TIDY)s
--variable STANDALONE_JAR:%(STANDALONE_JAR)s
--pythonpath %(PYTHONPATH)s
--include %(INCLUDE)s
--outputdir %(OUTPUTDIR)s
--output output.xml
--report report.html
--log log.html
--splitlog
--console dotted
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
'''.strip().split()

def atests(interpreter_path, *params):
    if interpreter_path == 'standalone':
        interpreter_path = jar()
    if interpreter_path.endswith('.jar'):
        return exec_standalone(interpreter_path, *params)
    return exec_interpreter(interpreter_path, *params)

def exec_interpreter(interpreter_path, *params):
    interpreter = _get_interpreter_basename(interpreter_path)
    resultdir, tempdir = _get_result_and_temp_dirs(interpreter)
    env = {
        'PYTHONPATH' : join(CURDIR, 'resources'),
        'OUTPUTDIR' : resultdir,
        'INTERPRETER': interpreter_path,
        'PYTHON': interpreter_path if 'python' in interpreter else '',
        'JYTHON': interpreter_path if 'jython' in interpreter else '',
        'IRONPYTHON': interpreter_path if 'ipy' in interpreter else '',
        'PLATFORM': sys.platform,
        'INCLUDE': 'jybot' if 'jython' in interpreter else 'pybot',
        'ROBOT': '%s %s' % (interpreter_path, RUNNER),
        'REBOT': '%s %s' % (interpreter_path, REBOT),
        'LIBDOC': '%s %s' % (interpreter_path, LIBDOC),
        'TESTDOC': '%s %s' % (interpreter_path, TESTDOC),
        'TIDY': '%s %s' % (interpreter_path, TIDY),
        'STANDALONE_JAR': ''
    }
    args = [arg % env for arg in ARGUMENTS]
    if sys.platform == 'darwin' and 'python' in interpreter:
        args += ['--exclude', 'x-exclude-on-osx-python']
    if 'ipy' in interpreter:
        args += ['--noncritical', 'x-fails-on-ipy']
    return _run(args, tempdir, *params)

def exec_standalone(standalone_path, *params):
    resultdir, tempdir = _get_result_and_temp_dirs('jython_standalone')
    tools_path = _get_bootclasspath()
    env = {
        'PYTHONPATH' : join(CURDIR, 'resources'),
        'OUTPUTDIR' : resultdir,
        'INTERPRETER': 'jython',
        'PYTHON': '',
        'JYTHON': '',
        'IRONPYTHON': '',
        'PLATFORM': sys.platform,
        'INCLUDE': 'jybot',
        'ROBOT': 'java %s -jar %s' % (tools_path, standalone_path),
        'REBOT': 'java %s -jar %s rebot' % (tools_path, standalone_path),
        'LIBDOC': 'java %s -jar %s libdoc' % (tools_path, standalone_path),
        'TESTDOC': 'java %s -jar %s testdoc' % (tools_path, standalone_path),
        'TIDY': 'java %s -jar %s tidy' % (tools_path, standalone_path),
        'STANDALONE_JAR': 'True'
    }
    args = [arg % env for arg in ARGUMENTS]
    args += ['--exclude', 'x-no-standalone']
    return _run(args, tempdir, *params)

def _get_bootclasspath():
    classpath = os.environ.get('CLASSPATH', '')
    if classpath:
        return '-Xbootclasspath/a:%s' % classpath
    return ''

def _run(args, tempdir, *params):
    if os.name == 'nt':
        args += ['--exclude', 'x-exclude-on-windows']
    command = [sys.executable, RUNNER]+args+list(params)
    environ = dict(os.environ, TEMPDIR=tempdir)
    print 'Running command\n%s\n' % ' '.join(command)
    sys.stdout.flush()
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    return subprocess.call(command, env=environ)

def _get_interpreter_basename(interpreter):
    interpreter = basename(interpreter)
    base, ext = splitext(interpreter)
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
