import sys
from os.path import abspath, dirname, join, normpath
import shutil


BASE = dirname(abspath(__file__))
ROOT = normpath(join(BASE, '..', '..', '..', '..'))
DATADIR = join(ROOT, 'atest', 'testdata', 'misc')
SRC = join(ROOT, 'src')
# must generate data next to testdoc.html to get relative sources correct
OUTPUT = join(BASE, '..', 'testdoc.js')
REAL_OUTPUT =  join(BASE, 'testdoc.js')

sys.path.insert(0, SRC)
from robot.testdoc import TestSuiteFactory, TestdocModelWriter

with open(OUTPUT, 'w') as output:
    TestdocModelWriter(output, TestSuiteFactory(DATADIR)).write_data()

shutil.move(OUTPUT, REAL_OUTPUT)

print REAL_OUTPUT

