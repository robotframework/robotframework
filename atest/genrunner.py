#!/usr/bin/env python

"""Script to generate atest runners based on data files.

Usage:  %s path/to/data.file
"""

from __future__ import with_statement
from os.path import abspath, basename, dirname, exists, join
import os
import sys

if len(sys.argv) != 2:
    print __doc__ % basename(sys.argv[0])
    sys.exit(1)

INPATH = abspath(sys.argv[1])
OUTPATH = INPATH.replace(join('atest', 'testdata'), join('atest', 'robot'))

if not exists(dirname(OUTPATH)):
    os.mkdir(dirname(OUTPATH))

with open(INPATH) as input:
    TESTS = []
    process = False
    for line in input.readlines():
        line = line.rstrip()
        if line.startswith('*'):
            name = line.replace('*', '').replace(' ', '').upper()
            process = name in ('TESTCASE', 'TESTCASES')
        elif process and line and line[0] != ' ':
            TESTS.append(line.split('  ')[0])

with open(OUTPATH, 'wb') as output:
    path = INPATH.split(join('atest', 'testdata'))[1][1:].replace(os.sep, '/')
    output.write("""\
*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    %(path)s
Force Tags       regression    pybot    jybot
Resource         atest_resource.txt

*** Test Cases ***

""" % locals())
    for test in TESTS:
        output.write(test + '\n    Check Test Case    ${TESTNAME}\n\n')

print OUTPATH
