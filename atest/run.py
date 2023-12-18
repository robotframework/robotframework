#!/usr/bin/env python3

"""A script for running Robot Framework's own acceptance tests.

Usage:  atest/run.py [-I name] [-S] [-R] [options] [data]

`data` is path (or paths) of the file or directory under the `atest/robot`
folder to execute. If `data` is not given, all tests except for tests tagged
with `no-ci` are executed.

Available `options` are in general normal Robot Framework options, but there
are some exceptions listed below.

By default, the same Python interpreter that is used for running this script is
also used for running tests. That can be changed by using the `--interpreter`
(`-I`) option. It can be the name of the interpreter like `pypy3` or a path to
the selected interpreter like `/usr/bin/python39`. If the interpreter itself
needs arguments, the interpreter and its arguments need to be quoted like
`"py -3.12"`.

To enable schema validation for all suites, use the `--schema-validation`
(`-S`) option. This is the same as setting the `ATEST_VALIDATE_OUTPUT`
environment variable to `TRUE`.

Use `--rerun-failed (`-R`)` to re-execute failed tests from the previous run.

Examples:
$ atest/run.py
$ atest/run.py --exclude no-ci atest/robot/standard_libraries
$ atest/run.py --interpreter pypy3
$ atest/run.py --rerun-failed

The results of the test execution are written into an interpreter specific
directory under the `atest/results` directory. Temporary outputs created
during the execution are created under the system temporary directory.
"""

import argparse
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from interpreter import Interpreter


CURDIR = Path(__file__).parent
LATEST = str(CURDIR / 'results/{interpreter.output_name}-latest.xml')
ARGUMENTS = '''
--doc Robot Framework acceptance tests
--metadata interpreter:{interpreter}
--variable-file {variable_file};{interpreter.path};{interpreter.name};{interpreter.version}
--pythonpath {pythonpath}
--output-dir {output_dir}
--splitlog
--console dotted
--console-width 100
--suite-stat-level 3
--log NONE
--report NONE
'''.strip()


def atests(interpreter, arguments, schema_validation=False):
    output_dir, temp_dir = _get_directories(interpreter)
    arguments = list(_get_arguments(interpreter, output_dir)) + list(arguments)
    rc = _run(arguments, temp_dir, interpreter, schema_validation)
    if rc < 251:
        _rebot(rc, output_dir, interpreter)
    return rc


def _get_directories(interpreter):
    name = interpreter.output_name
    output_dir = CURDIR / 'results' / name
    temp_dir = Path(tempfile.gettempdir()) / 'robotatest' / name
    if output_dir.exists():
        shutil.rmtree(output_dir)
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    return output_dir, temp_dir


def _get_arguments(interpreter, output_dir):
    arguments = ARGUMENTS.format(interpreter=interpreter,
                                 variable_file=CURDIR / 'interpreter.py',
                                 pythonpath=CURDIR / 'resources',
                                 output_dir=output_dir)
    for line in arguments.splitlines():
        yield from line.split(' ', 1)
    for exclude in interpreter.excludes:
        yield '--exclude'
        yield exclude


def _run(args, tempdir, interpreter, schema_validation):
    command = [str(c) for c in
               [sys.executable, CURDIR.parent / 'src/robot/run.py'] + args]
    environ = dict(os.environ,
                   TEMPDIR=str(tempdir),
                   PYTHONCASEOK='True',
                   PYTHONIOENCODING='')
    if schema_validation:
        environ['ATEST_VALIDATE_OUTPUT'] = 'TRUE'
    print(f"{interpreter}\n{interpreter.underline}\n")
    print(f"Running command:\n{' '.join(command)}\n")
    sys.stdout.flush()
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    return subprocess.call(command, env=environ)


def _rebot(rc, output_dir, interpreter):
    output = output_dir / 'output.xml'
    if rc == 0:
        print('All tests passed, not generating log or report.')
    else:
        command = [sys.executable, str(CURDIR.parent / 'src/robot/rebot.py'),
                   '--output-dir', str(output_dir), str(output)]
        subprocess.call(command)
    latest = Path(LATEST.format(interpreter=interpreter))
    latest.unlink(missing_ok=True)
    shutil.copy(output, latest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-I', '--interpreter', default=sys.executable)
    parser.add_argument('-S', '--schema-validation', action='store_true')
    parser.add_argument('-R', '--rerun-failed', action='store_true')
    parser.add_argument('-h', '--help', action='store_true')
    options, robot_args = parser.parse_known_args()
    try:
        interpreter = Interpreter(options.interpreter)
    except ValueError as err:
        sys.exit(str(err))
    if options.rerun_failed:
        robot_args[:0] = ['--rerun-failed', LATEST.format(interpreter=interpreter)]
    last = Path(robot_args[-1]) if robot_args else None
    source_given = last and (last.is_dir() or last.is_file() and last.suffix == '.robot')
    if not source_given:
        robot_args += ['--exclude', 'no-ci', CURDIR / 'robot']
    if options.help:
        print(__doc__)
        rc = 251
    else:
        rc = atests(interpreter, robot_args, options.schema_validation)
    sys.exit(rc)
