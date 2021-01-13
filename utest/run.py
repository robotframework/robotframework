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
import getopt
import os
import sys
import re
import unittest
import warnings


if not sys.warnoptions:
    warnings.simplefilter('always')
    warnings.filterwarnings('ignore', 'Not importing directory .*java', ImportWarning)


base = os.path.abspath(os.path.normpath(os.path.split(sys.argv[0])[0]))
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
    docs = False
    verbosity = 1
    try:
        options, args = getopt.getopt(argv, 'hH?vqd',
                                      ['help', 'verbose', 'quiet', 'doc'])
        if args:
            raise getopt.error('no arguments accepted, got %s' % list(args))
    except getopt.error as err:
        usage_exit(err)
    for opt, value in options:
        if opt in ('-h', '-H', '-?', '--help'):
            usage_exit()
        if opt in ('-q', '--quiet'):
            verbosity = 0
        if opt in ('-v', '--verbose'):
            verbosity = 2
        if opt in ('-d', '--doc'):
            docs = True
            verbosity = 2
    return docs, verbosity


def usage_exit(msg=None):
    print(__doc__)
    if msg is None:
        rc = 251
    else:
        print('\nError:', msg)
        rc = 252
    sys.exit(rc)


if __name__ == '__main__':
    docs, vrbst = parse_args(sys.argv[1:])
    tests = get_tests()
    suite = unittest.TestSuite(tests)
    runner = unittest.TextTestRunner(descriptions=docs, verbosity=vrbst)
    result = runner.run(suite)
    rc = len(result.failures) + len(result.errors)
    if rc > 250:
        rc = 250
    sys.exit(rc)
