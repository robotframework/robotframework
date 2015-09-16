#!/usr/bin/env python

"""Script to generate atest runners based on plain text data files.

Usage:  %s testdata/path/data.robot [robot/path/runner.robot]
"""

from os.path import abspath, basename, dirname, exists, join, splitext
import os
import sys

if len(sys.argv) not in [2, 3] or not all(a.endswith('.robot') for a in sys.argv[1:]):
    print __doc__ % basename(sys.argv[0])
    sys.exit(1)

INPATH = abspath(sys.argv[1])
if join('atest', 'testdata') not in INPATH:
    sys.exit("Input not under 'atest/testdata'.")
if len(sys.argv) == 2:
    OUTPATH = INPATH.replace(join('atest', 'testdata'), join('atest', 'robot'))
else:
    OUTPATH = sys.argv[2]

if not exists(dirname(OUTPATH)):
    os.mkdir(dirname(OUTPATH))

with open(INPATH) as input:
    TESTS = []
    process = False
    for line in input.readlines():
        line = line.rstrip()
        if line.startswith('*'):
            name = line.split('  ')[0].replace('*', '').replace(' ', '').upper()
            process = name in ('TESTCASE', 'TESTCASES')
        elif process and line and line[0] != ' ':
            TESTS.append(line.split('  ')[0])

with open(OUTPATH, 'wb') as output:
    path = INPATH.split(join('atest', 'testdata'))[1][1:].replace(os.sep, '/')
    output.write("""\
*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    %(path)s
Resource         atest_resource.robot

*** Test Cases ***
""" % locals())
    for test in TESTS:
        output.write(test + '\n    Check Test Case    ${TESTNAME}\n')
        if test is not TESTS[-1]:
            output.write('\n')

print OUTPATH
