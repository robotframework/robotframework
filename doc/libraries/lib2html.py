#!/usr/bin/env python

"""Usage:  lib2html.py [ library | all ]

Libraries:
  BuiltIn (bu)
  Collections (co)
  Dialogs (di)
  OperatingSystem (op)
  Screenshot (sc)
  String (st)
  Telnet (te)
"""

import sys
import tempfile
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.abspath(__file__),'..','..','..'))
LIBRARIES = {}
for line in __doc__.splitlines():
    res = re.search('(\w+) \((\w\w)\)', line)
    if res:
        name, alias = res.groups()
        LIBRARIES[name.lower()] = LIBRARIES[alias] = name

sys.path.insert(0, os.path.join(ROOT,'tools','libdoc'))
sys.path.insert(0, os.path.join(ROOT,'src'))

from libdoc import LibraryDoc, create_html_doc


def create_libdoc(name):
    ipath = os.path.join(ROOT,'src','robot','libraries',name+'.py')
    opath = os.path.join(ROOT,'doc','libraries',name+'.html')
    create_html_doc(LibraryDoc(ipath), opath)
    print opath


if __name__ == '__main__':
    try:
        name = sys.argv[1].lower()
        if name == 'all':
            for name in sorted(set(LIBRARIES.values())):
                create_libdoc(name)
        else:
            create_libdoc(LIBRARIES[name])
    except (IndexError, KeyError):
        print __doc__
