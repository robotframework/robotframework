#!/usr/bin/env python

"""Helper script to run all Robot Framework's unit tests.

usage: utest/run.py [options]

options:
    -q, --quiet     Minimal output
    -v, --verbose   Verbose output
    -d, --doc       Show test's doc string instead of name and class
                    (implies verbosity)
    -h, --help      Show help
"""

from __future__ import print_function
import unittest
import os
import sys
import re
import argparse


base = os.path.abspath(os.path.normpath(os.path.split(__file__)[0]))
for path in ['../src', '../atest/testresources/testlibs']:
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
    for name in sorted(os.listdir(directory)):
        if name.startswith("."):
            continue
        fullname = os.path.join(directory, name)
        if os.path.isdir(fullname):
            tests.extend(get_tests(fullname))
        elif testfile.match(name):
            modname = os.path.splitext(name)[0]
            if modname in imported:
                print("Test module '%s' imported both as '%s' and '%s'. "
                      "Rename one or fix test discovery."
                      % (modname, imported[modname],
                         os.path.join(directory, name)), file=sys.stderr)
                sys.exit(1)
            module = __import__(modname)
            imported[modname] = module.__file__
            tests.append(unittest.defaultTestLoader.loadTestsFromModule(module))
    return tests


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Helper script to run all Robot Framework's unit tests."
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("--verbose","-v", dest="verbosity", action="store_const", const=2, help="Minimal output")
    verbosity.add_argument("--quiet","-q", dest="verbosity", action="store_const", const=0, help="Verbose output")
    parser.set_defaults(verbosity=1)
    parser.add_argument("--doc", "-d", dest="doc", action="store_const", const=1, help="Show tets' doc string instaed of name and class. Implies verbosity")
    parser.set_defaults(doc=0)
    args = parser.parse_args()
    if args.doc == 1:
        args.verbosity = 2
    return args

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    tests = get_tests()
    suite = unittest.TestSuite(tests)
    runner = unittest.TextTestRunner(descriptions=args.doc, verbosity=args.verbosity)
    result = runner.run(suite)
    rc = len(result.failures) + len(result.errors)
    if rc > 250:
        rc = 250
    sys.exit(rc)
