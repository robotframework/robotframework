#!/usr/bin/env python

import sys
from os.path import abspath, dirname, join, normpath

BASE = dirname(abspath(__file__))
SRC = normpath(join(BASE, '..', '..', '..', '..', 'src'))
INPUT = join(BASE, 'libdoc_data.py')
OUTPUT = join(BASE, 'libdoc.js')

sys.path.insert(0, SRC)

from robot.libdoc import LibraryDocumentation

libdoc = LibraryDocumentation(INPUT)
libdoc.convert_docs_to_html()
with open(OUTPUT, 'w') as output:
    output.write('libdoc = ')
    output.write(libdoc.to_json())

print(OUTPUT)
