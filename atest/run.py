#!/usr/bin/env python3

"""A script for running Robot Framework's acceptance tests.

Usage:  atest/run.py interpreter [options] datasource(s)

Data sources are paths to directories or files under the `atest/robot` folder.

Available options are the same that can be used with Robot Framework.
See its help (e.g. `robot --help`) for more information.

The specified interpreter is used by acceptance tests under `atest/robot` to
run test cases under `atest/testdata`. It can be the name of the interpreter
like (e.g. `python` or `jython`, a path to the selected interpreter like
`/usr/bin/python36`, or a path to the standalone jar distribution (e.g.
`dist/robotframework-3.2b3.dev1.jar`). The standalone jar needs to be
separately created with `invoke jar`.

If the interpreter itself needs arguments, the interpreter and its arguments
need to be quoted like `"py -3"`.

Note that this script itself must always be executed with Python 3.6 or newer.

Examples:
$ atest/run.py python --test example atest/robot
$ atest/run.py /opt/jython27/bin/jython atest/robot/tags/tag_doc.robot
> atest\\run.py "py -3" -e no-ci atest\\robot
"""

import os
import shutil
import signal
import subprocess
import sys
import tempfile
from os.path import abspath, dirname, exists, join, normpath

from interpreter import InterpreterFactory


CURDIR = dirname(abspath(__file__))
ARGUMENTS = '''
--doc Robot Framework acceptance tests
--metadata interpreter:{interpreter}
--variablefile {variable_file};{interpreter.path};{interpreter.name};{interpreter.version}
--pythonpath {pythonpath}
--outputdir {outputdir}
--splitlog
--console dotted
--consolewidth 100
--SuiteStatLevel 3
--TagStatExclude no-*
'''.strip()


def atests(interpreter, *arguments):
    try:
        interpreter = InterpreterFactory(interpreter)
    except ValueError as err:
        sys.exit(err)
    outputdir, tempdir = _get_directories(interpreter)
    arguments = list(_get_arguments(interpreter, outputdir)) + list(arguments)
    return _run(arguments, tempdir, interpreter)


def _get_directories(interpreter):
    name = interpreter.output_name
    outputdir = dos_to_long(join(CURDIR, 'results', name))
    tempdir = dos_to_long(join(tempfile.gettempdir(), 'robottests', name))
    if exists(outputdir):
        shutil.rmtree(outputdir)
    if exists(tempdir):
        shutil.rmtree(tempdir)
    os.makedirs(tempdir)
    return outputdir, tempdir


def _get_arguments(interpreter, outputdir):
    arguments = ARGUMENTS.format(interpreter=interpreter,
                                 variable_file=join(CURDIR, 'interpreter.py'),
                                 pythonpath=join(CURDIR, 'resources'),
                                 outputdir=outputdir)
    for line in arguments.splitlines():
        for part in line.split(' ', 1):
            yield part
    for exclude in interpreter.excludes:
        yield '--exclude'
        yield exclude


def _run(args, tempdir, interpreter):
    runner = normpath(join(CURDIR, '..', 'src', 'robot', 'run.py'))
    command = [sys.executable, runner] + args
    environ = dict(os.environ,
                   TEMPDIR=tempdir,
                   CLASSPATH=interpreter.classpath or '',
                   JAVA_OPTS=interpreter.java_opts or '',
                   PYTHONCASEOK='True',
                   PYTHONIOENCODING='')
    print('%s\n%s\n' % (interpreter, '-' * len(str(interpreter))))
    print('Running command:\n%s\n' % ' '.join(command))
    sys.stdout.flush()
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    return subprocess.call(command, env=environ)


def dos_to_long(path):
    """Convert Windows paths in DOS format (e.g. exampl~1.txt) to long format.

    This is done to avoid problems when later comparing paths. Especially
    IronPython handles DOS paths inconsistently.
    """
    if not (os.name == 'nt' and '~' in path and os.path.exists(path)):
        return path
    from ctypes import create_unicode_buffer, windll
    buf = create_unicode_buffer(500)
    windll.kernel32.GetLongPathNameW(path, buf, 500)
    return buf.value


if __name__ == '__main__':
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print(__doc__)
        rc = 251
    else:
        rc = atests(*sys.argv[1:])
    sys.exit(rc)
