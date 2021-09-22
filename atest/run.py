#!/usr/bin/env python3

r"""A script for running Robot Framework's acceptance tests.

Usage:  atest/run.py interpreter [options] datasource(s)

Data sources are paths to directories or files under the `atest/robot` folder.

Available options are the same that can be used with Robot Framework.
See its help (e.g. `robot --help`) for more information.

The specified interpreter is used by acceptance tests under `atest/robot` to
run test cases under `atest/testdata`. It can be the name of the interpreter
like (e.g. `python` or `py -3.9`) or a path to the selected interpreter like
(e.g. `/usr/bin/python39`).

If the interpreter itself needs arguments, the interpreter and its arguments
need to be quoted like `"py -3"`.

Examples:
$ atest/run.py python --test example atest/robot
> atest\run.py "py -3.9" -e no-ci atest\robot\running
"""

import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

from interpreter import Interpreter


CURDIR = Path(__file__).parent
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
'''.strip()


def atests(interpreter, *arguments):
    try:
        interpreter = Interpreter(interpreter)
    except ValueError as err:
        sys.exit(err)
    outputdir, tempdir = _get_directories(interpreter)
    arguments = list(_get_arguments(interpreter, outputdir)) + list(arguments)
    return _run(arguments, tempdir, interpreter)


def _get_directories(interpreter):
    name = interpreter.output_name
    outputdir = CURDIR / 'results' / name
    tempdir = Path(tempfile.gettempdir()) / 'robotatest' / name
    if outputdir.exists():
        shutil.rmtree(outputdir)
    if tempdir.exists():
        shutil.rmtree(tempdir)
    os.makedirs(tempdir)
    return outputdir, tempdir


def _get_arguments(interpreter, outputdir):
    arguments = ARGUMENTS.format(interpreter=interpreter,
                                 variable_file=CURDIR / 'interpreter.py',
                                 pythonpath=CURDIR / 'resources',
                                 outputdir=outputdir)
    for line in arguments.splitlines():
        for part in line.split(' ', 1):
            yield part
    for exclude in interpreter.excludes:
        yield '--exclude'
        yield exclude


def _run(args, tempdir, interpreter):
    command = [sys.executable, str(CURDIR.parent / 'src/robot/run.py')] + args
    environ = dict(os.environ,
                   TEMPDIR=str(tempdir),
                   PYTHONCASEOK='True',
                   PYTHONIOENCODING='')
    print('%s\n%s\n' % (interpreter, '-' * len(str(interpreter))))
    print('Running command:\n%s\n' % ' '.join(command))
    sys.stdout.flush()
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    return subprocess.call(command, env=environ)


if __name__ == '__main__':
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print(__doc__)
        rc = 251
    else:
        rc = atests(*sys.argv[1:])
    sys.exit(rc)
