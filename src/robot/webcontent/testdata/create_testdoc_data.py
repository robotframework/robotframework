import sys
from os.path import abspath, dirname, join, normpath

BASE = dirname(abspath(__file__))
ROOT = normpath(join(BASE, '..', '..', '..', '..'))
DATADIR = join(ROOT, 'atest', 'testdata', 'misc')
SRC = join(ROOT, 'src')
OUTPATH = join(BASE, 'testdoc.js')

sys.path.insert(0, SRC)
from robot.testdoc import TestSuiteFactory, TestdocModelWriter

with open(OUTPATH, 'w') as output:
    TestdocModelWriter(output, TestSuiteFactory(DATADIR)).write_data()

print OUTPATH

