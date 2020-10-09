#!/usr/bin/env python

from __future__ import print_function

import sys
from os.path import abspath, dirname, join, normpath

BASE = dirname(abspath(__file__))
SRC = normpath(join(BASE, '..', '..', '..', '..', 'src'))
# must generate data next to testdoc.html to get relative sources correct
INPUT = join(BASE, 'libdoc.txt')
OUTPUT = join(BASE, 'libdoc.js')

sys.path.insert(0, SRC)

from robot.libdoc import LibraryDocumentation
from robot.libdocpkg.htmlwriter import LibdocModelWriter

with open(OUTPUT, 'w') as output:
    libdoc = LibraryDocumentation(INPUT)
    LibdocModelWriter(output, libdoc).write_data()

print(OUTPUT)
