#!/usr/bin/env python

"""Helper script to run all Robot Framework's unit tests.

usage: run_utest.py [options]

options:
    -q, --quiet     Minimal output
    -v, --verbose   Verbose output
    -d, --doc       Show test's doc string instead of name and class
                    (implies verbosity)
    -h, --help      Show help
"""

import unittest
import os
import sys
import re
import getopt
import shutil
import subprocess
from os.path import join, abspath, dirname


# Check for new working dir after 2to3:
if not 'UTESTDIR' in globals():
    # ==> still the original script before 2to3.
    UTESTDIR = dirname(abspath(__file__))
ROBOTDIR = join(UTESTDIR, '..', 'src', 'robot')
ATESTDIR = join(UTESTDIR, '..', 'atest')

# If run with Python 3:
# - Copy src/robot/ and atest/ to atest/python3/
# - Run 2to3
# - Exec this file's copy in-place for actual testing

# Is this script already the Python 3 copy?
if not 'do2to3' in globals():
    # ==> still the original.
    do2to3 = True
if sys.version_info[0] == 3 and do2to3:
    PY3DIR = join(UTESTDIR, 'python3')
    PY3UTESTDIR = join(PY3DIR, 'utest')
    PY3ATESTDIR = join(PY3DIR, 'atest')

    shutil.rmtree((PY3DIR), ignore_errors=True)
    os.makedirs(join(PY3DIR, 'src'))
    shutil.copytree(ROBOTDIR, join(PY3DIR, 'src', 'robot'), symlinks=True)
    shutil.copytree(
      UTESTDIR, PY3UTESTDIR, symlinks=True,
      ignore=lambda src, names: names if src == PY3DIR else []
      )
    shutil.copytree( # ATESTDIR, PY3ATESTDIR, symlinks=True)
      ATESTDIR, PY3ATESTDIR, symlinks=True,
      ignore=lambda src, names: names if src == join(ATESTDIR, 'python3') else []
      )
    status = subprocess.call(
      ['2to3', '--no-diffs', '-n', '-w',
       '-x', 'dict',
       '-x', 'filter',
       PY3DIR
       ])
    if status:
        sys.exit(status)

    do2to3 = False
    UTESTDIR = PY3UTESTDIR

    # Exec this file's Python 3 copy:
    TESTRUNNER = join(UTESTDIR, 'run_utests.py')
    exec(open(TESTRUNNER).read())
    sys.exit(0)


base = UTESTDIR
## base = os.path.abspath(os.path.normpath(os.path.split(sys.argv[0])[0]))
for path in ['../src', '../src/robot/libraries', '../src/robot',
             '../atest/testresources/testlibs' ]:
    path = os.path.join(base, path.replace('/', os.sep))
    if path not in sys.path:
        sys.path.insert(0, path)

testfile = re.compile("^test_.*\.py$", re.IGNORECASE)
imported = {}

def get_tests(directory=None):
    if directory is None:
        directory = base
    sys.path.insert(0, directory)
    tests = []
    for name in os.listdir(directory):
        if name.startswith("."): continue
        fullname = os.path.join(directory, name)
        if os.path.isdir(fullname):
            tests.extend(get_tests(fullname))
        elif testfile.match(name):
            modname = os.path.splitext(name)[0]
            if modname in imported:
                sys.stderr.write("Test module '%s' imported both as '%s' and "
                                 "'%s'.\nRename one or fix test discovery.\n"
                                 % (modname, imported[modname],
                                    os.path.join(directory, name)))
                sys.exit(1)
            module = __import__(modname)
            imported[modname] = module.__file__
            tests.append(unittest.defaultTestLoader.loadTestsFromModule(module))
    return tests


def parse_args(argv):
    docs = 0
    verbosity = 1
    try:
        options, args = getopt.getopt(argv, 'hH?vqd',
                                      ['help','verbose','quiet','doc'])
        if len(args) != 0:
            raise getopt.error('no arguments accepted, got %s' % (args))
    except getopt.error:
        usage_exit(sys.exc_info()[1])
    for opt, value in options:
        if opt in ('-h','-H','-?','--help'):
            usage_exit()
        if opt in ('-q','--quit'):
            verbosity = 0
        if opt in ('-v', '--verbose'):
            verbosity = 2
        if opt in ('-d', '--doc'):
            docs = 1
            verbosity = 2
    return docs, verbosity


def usage_exit(msg=None):
    print(__doc__)
    if msg is None:
        rc = 251
    else:
        print('\nError: %s' % msg)
        rc = 252
    sys.exit(rc)


if __name__ == '__main__':
    docs, vrbst = parse_args(sys.argv[1:])
    tests = get_tests()
    suite = unittest.TestSuite(tests)
    runner = unittest.TextTestRunner(descriptions=docs, verbosity=vrbst)
    result = runner.run(suite)
    rc = len(result.failures) + len(result.errors)
    if rc > 250: rc = 250
    sys.exit(rc)
