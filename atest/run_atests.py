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

import re
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from os.path import abspath, basename, dirname, exists, join, normpath, splitext

if sys.version_info < (2, 6):
    sys.exit('Running this script requires Python 2.6 or newer.')

try:
    CURDIR = CURDIR
except NameError:
    CURDIR = dirname(abspath(__file__))
ROBOTDIR = join(CURDIR, '..', 'src', 'robot')

# If run with Python 3:
# - Copy src/robot/ and atest/ to atest/python3/
# - Run 2to3
# - Modify Python literals in Suite/Resource .txt files
# - Exec this file's copy in-place for actual testing
try:
    # Is this file already the Python 3 copy or the original?
    do2to3 = do2to3
except NameError:
    do2to3 = True
if sys.version_info[0] == 3 and do2to3:
    PY3DIR = join(CURDIR, 'python3')
    PY3ATESTDIR = join(PY3DIR, 'atest')

    shutil.rmtree((PY3DIR), ignore_errors=True)
    os.makedirs(join(PY3DIR, 'src'))
    shutil.copytree(ROBOTDIR, join(PY3DIR, 'src', 'robot'), symlinks=True)
    shutil.copytree(
      CURDIR, join(PY3ATESTDIR), symlinks=True,
      ignore=lambda src, names: names if src == PY3DIR else []
      )
    status = subprocess.call(
      ['2to3', '--no-diffs', '-n', '-w',
       '-x', 'dict',
       '-x', 'filter',
       PY3DIR
       ])
    if status:
        sys.exit(status)

    # Modify the Suite/Resource .txt files:
    for atest_dirname in ['testdata', 'robot']:
        for dirpath, dirnames, filenames in os.walk(
          join(PY3ATESTDIR, atest_dirname)
          ):
            for filename in filenames:
                if filename.endswith('.txt'):
                    path = join(dirpath, filename)
                    try:
                        with open(path) as f:
                            text = f.read()
                    except UnicodeDecodeError:
                        pass
                    else:
                        print("Preparing for Python 3: %s" % path)
                        # Remove u prefixes from unicode literals:
                        text = re.sub(r'([\[(= ])u\'', r'\1\'', text)
                        # Replace hex codes in strings
                        # with actual unicode characters,
                        # if not used to create bytes objects:
                        text = re.sub(
                          r'\\\\x([0-9a-f]{2})',
                          lambda match: (
                            chr(int(match.group(1), 16))
                            if match.group(1) >= '80'
                            else match.group(0)),
                          text)
                        text = re.sub(
                          r'\\\\u([0-9a-f]{4})',
                          lambda match: chr(int(match.group(1), 16)),
                          text)
                        # Remove L suffixes from integer literals:
                        text = re.sub(r'([1-9][0-9]+)L', r'\1', text)
                        with open(path, 'w') as f:
                            f.write(text)

    do2to3 = False
    CURDIR = PY3ATESTDIR

    # Redirect the Test Suite arg to the Python3 copy:
    sys.argv[-1] = join(CURDIR, sys.argv[-1])

    # Exec this file's Python 3 copy:
    TESTRUNNER = join(CURDIR, 'run_atests.py')
    exec(open(TESTRUNNER).read())
    sys.exit(0)

RUNNER = normpath(join(CURDIR, '..', 'src', 'robot', 'run.py'))
ARGUMENTS = ' '.join('''
--doc RobotSPFrameworkSPacceptanceSPtests
--reporttitle RobotSPFrameworkSPTestSPReport
--logtitle RobotSPFrameworkSPTestSPLog
--metadata Interpreter:%(INTERPRETER)s
--metadata Platform:%(PLATFORM)s
--variable INTERPRETER:%(INTERPRETER)s
--variable PYTHON:%(PYTHON)s
--variable PYTHON3:%(PYTHON3)s
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
        'PYTHON3': interpreter_path
                   if 'python' in interpreter and sys.version_info[0] == 3
                   else '',
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
    print('Running command\n%s\n' % command)
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
        print(__doc__)
        rc = 251
    else:
        rc = atests(*sys.argv[1:])
    sys.exit(rc)
