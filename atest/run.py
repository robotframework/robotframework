#!/usr/bin/env python3

"""A script for running Robot Framework's own acceptance tests.

Usage:  atest/run.py [--interpreter name] [--schema-validation [options] [data]

`data` is path (or paths) of the file or directory under the `atest/robot`
folder to execute. If `data` is not given, all tests except for tests tagged
with `no-ci` are executed.

Available `options` are the same that can be used with Robot Framework.
See its help (e.g. `robot --help`) for more information.

By default, uses the same Python interpreter for running tests that is used
for running this script. That can be changed by using the `--interpreter`
(`-I`) option. It can be the name of the interpreter like `pypy3` or a path
to the selected interpreter like `/usr/bin/python39`. If the interpreter
itself needs arguments, the interpreter and its arguments need to be quoted
like `"py -3.9"`.

To enable schema validation for all suites, use `--schema-validation` (`-S`)
option. This is same as setting `ATEST_VALIDATE_OUTPUT` environment variable
to `TRUE`.

Examples:
$ atest/run.py
$ atest/run.py --exclude no-ci atest/robot/standard_libraries
$ atest/run.py --interpreter pypy3

The results of the test execution are written into an interpreter specific
directory under the `atest/results` directory. Temporary outputs created
during the execution are created under the system temporary directory.
"""

import argparse
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


def atests(interpreter, arguments, schema_validation=False):
    try:
        interpreter = Interpreter(interpreter)
    except ValueError as err:
        sys.exit(err)
    outputdir, tempdir = _get_directories(interpreter)
    arguments = list(_get_arguments(interpreter, outputdir)) + list(arguments)
    return _run(arguments, tempdir, interpreter, schema_validation)


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
        yield from line.split(' ', 1)
    for exclude in interpreter.excludes:
        yield '--exclude'
        yield exclude


def _run(args, tempdir, interpreter, schema_validation):
    command = [sys.executable, str(CURDIR.parent / 'src/robot/run.py')] + args
    environ = dict(os.environ,
                   TEMPDIR=str(tempdir),
                   PYTHONCASEOK='True',
                   PYTHONIOENCODING='')
    if schema_validation:
        environ['ATEST_VALIDATE_OUTPUT'] = 'TRUE'
    print('%s\n%s\n' % (interpreter, '-' * len(str(interpreter))))
    print('Running command:\n%s\n' % ' '.join(command))
    sys.stdout.flush()
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    return subprocess.call(command, env=environ)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-I', '--interpreter', default=sys.executable)
    parser.add_argument('-S', '--schema-validation', action='store_true')
    parser.add_argument('-h', '--help', action='store_true')
    options, robot_args = parser.parse_known_args()
    if not robot_args or not Path(robot_args[-1]).exists():
        robot_args += ['--exclude', 'no-ci', str(CURDIR/'robot')]
    if options.help:
        print(__doc__)
        rc = 251
    else:
        rc = atests(options.interpreter, robot_args, options.schema_validation)
    sys.exit(rc)
