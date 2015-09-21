#!/usr/bin/env python

"""A script for running Robot Framework's acceptance tests.

Usage:  run_atests.py interpreter [options] datasource(s)

Data sources are paths to directories or files under the `atest/robot` folder.

Available options are the same that can be used with Robot Framework.
See its help (e.g. `pybot --help`) for more information.

The specified interpreter is used by acceptance tests under `atest/robot` to
run test cases under `atest/testdata`. It can be simply `python` or `jython`
(if they are in PATH) or a path to a selected interpreter (e.g.
`/usr/bin/python26`) or a path to a robotframework standalone jar (e.g.
`dist/robotframework-2.9dev234.jar`).

As a special case the interpreter value `standalone` will compile a new
standalone jar from the current sources and execute the acceptance tests with
it.

Note that this script itself must always be executed with Python 2.7.

Examples:
$ atest/run_atests.py python --test example atest/robot
$ atest/run_atests.py /opt/jython27/bin/jython atest/robot/tags/tag_doc.robot
"""

import os
import shutil
import signal
import subprocess
import sys
import tempfile
from os.path import abspath, dirname, exists, join, normpath


CURDIR = dirname(abspath(__file__))
SRC = normpath(join(CURDIR, '..', 'src', 'robot'))
RUNNER = join(SRC, 'run.py')
REBOT = join(SRC, 'rebot.py')
TESTDOC = join(SRC, 'testdoc.py')
LIBDOC = join(SRC, 'libdoc.py')
TIDY = join(SRC, 'tidy.py')


sys.path.append(join(CURDIR, '..'))
try:
    from tasks import jar
except ImportError:
    def jar(*args, **kwargs):
        raise RuntimeError("Creating jar distribution requires 'invoke'.")


ARGUMENTS = '''
--doc Robot Framework acceptance tests
--metadata Interpreter:{interpreter_name} {interpreter_version}
--metadata Platform:{platform}
--variable INTERPRETER:{interpreter}
--variable PYTHON:{python}
--variable JYTHON:{jython}
--variable IRONPYTHON:{ironpython}
--variable ROBOT:{robot}
--variable REBOT:{rebot}
--variable LIBDOC:{libdoc}
--variable TESTDOC:{testdoc}
--variable TIDY:{tidy}
--variable STANDALONE_JAR:{standalone_jar}
--pythonpath {pythonpath}
--outputdir {outputdir}
--splitlog
--console dotted
--SuiteStatLevel 3
--TagStatExclude no-*
'''.strip()


def atests(interpreter_path, *params):
    if interpreter_path == 'standalone':
        interpreter_path = jar()
    if interpreter_path.endswith('.jar'):
        return exec_standalone(interpreter_path, *params)
    return exec_interpreter(interpreter_path, *params)


def exec_interpreter(interpreter, *params):
    interpreter_name, interpreter_version = _get_name_and_version(interpreter)
    outputdir, tempdir = _get_directories(interpreter_name)
    args = list(_get_arguments(interpreter, interpreter_name,
                               interpreter_version, outputdir))
    for exclude in _get_excludes(interpreter_name, interpreter_version):
        args += ['--exclude', exclude]
    return _run(args, tempdir, *params)


def _get_arguments(interpreter, interpreter_name, interpreter_version, outputdir):
    arguments = ARGUMENTS.format(
        pythonpath=join(CURDIR, 'resources'),
        outputdir=outputdir,
        interpreter=interpreter,
        interpreter_name=interpreter_name,
        interpreter_version=interpreter_version,
        python=interpreter if interpreter_name == 'Python' else '',
        jython=interpreter if interpreter_name == 'Jython' else '',
        ironpython=interpreter if interpreter_name == 'IronPython' else '',
        platform=sys.platform,
        robot=' '.join([interpreter, RUNNER]),
        rebot=' '.join([interpreter, REBOT]),
        libdoc=' '.join([interpreter, LIBDOC]),
        testdoc=' '.join([interpreter, TESTDOC]),
        tidy=' '.join([interpreter, TIDY]),
        standalone_jar=''
    )
    for line in arguments.splitlines():
        for part in line.split(' ', 1):
            yield part


#FIXME: Clean this horror up.
def _get_excludes(interpreter, version):
    if interpreter == 'IronPython':
        yield 'no-ipy'
        yield 'require-et13'
        yield 'require-lxml'
        yield 'require-docutils'  # https://github.com/IronLanguages/main/issues/1230
    if interpreter == 'Jython':
        yield 'no-jython'
        yield 'require-lxml'
    else:
        yield 'require-jython'
    if interpreter == 'Python':
        if sys.platform == 'darwin':
            yield 'no-osx-python'
        if version == '2.6':
            yield 'no-python26'
            yield 'require-et13'
    if os.name == 'nt':
        yield 'no-windows'
        if version == '2.6':
            yield 'no-windows-python26'
        if interpreter == 'Jython':
            yield 'no-windows-jython'
    if sys.platform == 'darwin':
        yield 'no-osx'


def exec_standalone(standalone_path, *params):
    outputdir, tempdir = _get_directories('jython_standalone')
    args = list(_get_standalone_arguments(standalone_path, outputdir))
    args += ['--exclude', 'no-standalone', '--exclude', 'no-jython',
             '--exclude', 'require-lxml', '--exclude', 'require-docutils',
             '--exclude', 'require-yaml']
    if os.name == 'nt':
        args += ['--exclude', 'no-windows']
    if sys.platform == 'darwin':
        args += ['--exclude', 'no-osx']
    return _run(args, tempdir, *params)

def _get_standalone_arguments(standalone_path, outputdir):
    tools_path = _get_bootclasspath()
    arguments = ARGUMENTS.format(
        pythonpath=join(CURDIR, 'resources'),
        outputdir=outputdir,
        interpreter='jython',   # ???
        interpreter_name='standalone',
        interpreter_version='',
        python='',
        jython='',
        ironpython='',
        platform=sys.platform,
        robot='java %s -jar %s' % (tools_path, standalone_path),
        rebot='java %s -jar %s rebot' % (tools_path, standalone_path),
        libdoc='java %s -jar %s libdoc' % (tools_path, standalone_path),
        testdoc='java %s -jar %s testdoc' % (tools_path, standalone_path),
        tidy='java %s -jar %s tidy' % (tools_path, standalone_path),
        standalone_jar='True'
    )
    for line in arguments.splitlines():
        for part in line.split(' ', 1):
            yield part

def _get_bootclasspath():
    classpath = os.environ.get('CLASSPATH', '')
    if classpath:
        return '-Xbootclasspath/a:%s' % classpath
    return ''

def _run(args, tempdir, *params):
    command = [sys.executable, RUNNER]+args+list(params)
    environ = dict(os.environ, TEMPDIR=tempdir)
    print 'Running command\n%s\n' % ' '.join(command)
    sys.stdout.flush()
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    return subprocess.call(command, env=environ)

def _get_name_and_version(interpreter):
    try:
        output = subprocess.check_output([interpreter, '-V'],
                                         stderr=subprocess.STDOUT)
    except OSError:
        sys.exit('Invalid interpreter: %s' % interpreter)
    name, version = output.split()[:2]
    version = '.'.join(version.split('.')[:2])
    return name, version

def _get_directories(interpreter):
    interpreter = interpreter.lower()
    resultdir = join(CURDIR, 'results', interpreter)
    tempdir = join(tempfile.gettempdir(), 'robottests', interpreter)
    resultdir = dos_to_long(resultdir)
    tempdir = dos_to_long(tempdir)
    if exists(resultdir):
        shutil.rmtree(resultdir)
    if exists(tempdir):
        shutil.rmtree(tempdir)
    os.makedirs(tempdir)
    return resultdir, tempdir


def dos_to_long(path):
    """Convert Windows paths in DOS format (e.g. exampl~1.txt) to long format.

    This is done to avoid problems when later comparing paths. Especially
    IronPython handles DOS paths inconsistently.
    """
    if not (os.name == 'nt' and '~' in path and os.path.exists(path)):
        return path
    from ctypes import create_unicode_buffer, windll
    buf = create_unicode_buffer(500)
    windll.kernel32.GetLongPathNameW(path.decode('mbcs'), buf, 500)
    return buf.value.encode('mbcs')


if __name__ == '__main__':
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print __doc__
        rc = 251
    else:
        rc = atests(*sys.argv[1:])
    sys.exit(rc)
