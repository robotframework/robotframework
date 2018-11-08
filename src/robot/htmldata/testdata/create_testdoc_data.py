#!/usr/bin/env python

from __future__ import print_function

import sys
from os.path import abspath, dirname, join, normpath
import shutil

BASE = dirname(abspath(__file__))
ROOT = normpath(join(BASE, '..', '..', '..', '..'))
DATA = [join(ROOT, 'atest', 'testdata', 'misc'), join(BASE, 'dir.suite')]
SRC = join(ROOT, 'src')
# must generate data next to testdoc.html to get relative sources correct
OUTPUT = join(BASE, '..', 'testdoc.js')
REAL_OUTPUT =  join(BASE, 'testdoc.js')

sys.path.insert(0, SRC)

from robot.testdoc import TestSuiteFactory, TestdocModelWriter

with open(OUTPUT, 'w') as output:
    TestdocModelWriter(output, TestSuiteFactory(DATA)).write_data()

shutil.move(OUTPUT, REAL_OUTPUT)

print(REAL_OUTPUT)

