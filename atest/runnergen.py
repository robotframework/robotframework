#!/usr/bin/env python

"""runnergen.py -- A script to generate atest runners based on data files.

Usage:  runnergen.py path/to/data.file
"""

from __future__ import with_statement
import sys, os

if len(sys.argv) != 2:
    print __doc__
    sys.exit(1)

inpath = os.path.abspath(sys.argv[1])
outpath = inpath.replace(os.path.join('atest', 'testdata'), 
                         os.path.join('atest', 'robot'))

with open(inpath) as input:
    tests = []
    process = False
    for line in input.readlines():
        line = line.rstrip()
        if line.startswith('*'):
            name = line.replace('*', '').replace(' ', '').upper()
            process = name in ('TESTCASE', 'TESTCASES')
        elif process and line and line[0] != ' ':
            tests.append(line.split('  ')[0])

with open(outpath, 'w') as output:
    path = inpath.split(os.path.join('atest', 'testdata'))[1][1:]
    output.write("""*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  %s
Force Tags      regression  pybot  jybot
Resource        %s/resources/resource.txt

*** Test Cases ***

""" % (path.replace(os.sep, '/'), '/'.join(['..']*path.count(os.sep))))
    for test in tests:
        output.write(test + '\n    Check Test Case  ${TESTNAME}\n\n')

print outpath
