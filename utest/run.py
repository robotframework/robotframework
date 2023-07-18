#!/usr/bin/env python

"""Helper script to run all Robot Framework's unit tests.

usage: utest/run.py [options] [directory]

options:
    -q, --quiet     Minimal output
    -v, --verbose   Verbose output
    -d, --doc       Show test's doc string instead of name and class
                    (implies verbosity)
    -h, --help      Show help

`directory` is the path of the directory under the `utest` folder to execute.
If no value is given all tests are run

examples:
$ utest/run.py -q output
This will run only the unit tests in the subdirectory output
"""

import argparse
import os
import sys
import re
import unittest
import warnings


if not sys.warnoptions:
    warnings.simplefilter('always')


base = os.path.abspath(os.path.normpath(os.path.split(sys.argv[0])[0]))
for path in ['../src', '../atest/testresources/testlibs', '../utest/resources']:
    path = os.path.join(base, path.replace('/', os.sep))
    if path not in sys.path:
        sys.path.insert(0, path)

testfile = re.compile(r"^test_.*\.py$", re.IGNORECASE)
imported = {}


def get_tests(directory=None):
    if directory is None:
        directory = base
    else:
        directory = os.path.join(base, directory)
    sys.path.insert(0, directory)
    tests = []
    for name in sorted(os.listdir(directory)):
        if name.startswith("."):
            continue
        fullname = os.path.join(directory, name)
        if os.path.isdir(fullname):
            tests.extend(get_tests(fullname))
        elif testfile.match(name):
            modname = os.path.splitext(name)[0]
            if modname in imported:
                print(
                    f"Test module '{modname}' imported both as '{imported[modname]}' and "
                    + "'{os.path.join(directory, name)}'. Rename one or fix test discovery.",
                    file=sys.stderr,
                )
                sys.exit(1)
            module = __import__(modname)
            imported[modname] = module.__file__
            tests.append(unittest.defaultTestLoader.loadTestsFromModule(module))
    return tests


def usage_exit(msg=None):
    print(__doc__)
    if msg is None:
        rc = 251
    else:
        print('\nError:', msg)
        rc = 252
    sys.exit(rc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False, description=__doc__)
    parser.add_argument("-I", "--interpreter", default=sys.executable)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-q", "--quiet", dest="vrbst", action="store_const", const=0)
    parser.add_argument("-v", "--verbose",dest="vrbst", action="store_const", const=2)
    parser.add_argument("-d", "--doc", dest="docs", action="store_true")
    parser.add_argument("-x", "--exit-on-failure", dest="failfast", action="store_true")
    parser.add_argument(dest="directory", nargs="?", action="store", default=None)
    parser.set_defaults(vrbst=1)

    args = parser.parse_args()
    if args.docs:
        args.vrbst = 2
    if args.help:
        usage_exit()

    tests = get_tests(args.directory)
    suite = unittest.TestSuite(tests)
    runner = unittest.TextTestRunner(descriptions=args.docs, verbosity=args.vrbst,
                                     failfast=args.failfast)
    result = runner.run(suite)
    rc = len(result.failures) + len(result.errors)
    if rc > 250:
        rc = 250
    sys.exit(rc)
