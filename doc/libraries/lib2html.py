#!/usr/bin/env python

"""Usage:  lib2html.py [ library | all ]

Libraries:
  BuiltIn (bu)
  Collections (co)
  DateTime (da)
  Dialogs (di)
  OperatingSystem (op)
  Process (pr)
  Screenshot (sc)
  String (st)
  Telnet (te)
  XML (xm)
"""

from os.path import abspath, dirname, join
import sys
import re


ROOT = dirname(dirname(dirname(abspath(__file__))))
sys.path.insert(0, join(ROOT, 'src'))

from robot.libdoc import libdoc


LIBRARIES = {}
for line in __doc__.splitlines():
    res = re.search('\s+(\w+) \((\w+)\)', line)
    if res:
        name, alias = res.groups()
        LIBRARIES[name.lower()] = LIBRARIES[alias] = name


def create_libdoc(name):
    libdoc(name, join(ROOT, 'doc', 'libraries', name+'.html'))


def create_all():
    for name in sorted(set(LIBRARIES.values())):
        create_libdoc(name)


if __name__ == '__main__':
    try:
        name = sys.argv[1].lower()
        if name == 'all':
            create_all()
        else:
            create_libdoc(LIBRARIES[name])
    except (IndexError, KeyError):
        print __doc__
