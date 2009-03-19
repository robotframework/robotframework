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
    if name == 'Screenshot':
       javamods = _FakeJavaModules()
    ipath = os.path.join(ROOT,'src','robot','libraries',name+'.py')
    opath = os.path.join(ROOT,'doc','libraries',name+'.html')
    create_html_doc(LibraryDoc(ipath), opath)
    if name == 'Screenshot':
        javamods.cleanup()
    print opath


class _FakeJavaModules:

    """Adds fake Java modules to sys.modules to enable importing Screenshot"""

    __path__ = [tempfile.gettempdir()]

    def __init__(self):
        self._fake_module_paths = []
        self.create_module('awt', ['Toolkit', 'Robot', 'Rectangle'])
        self.create_module('io', ['File'])
        self.create_module('imageio', ['ImageIO'])
        sys.modules['java'] = self
        sys.modules['javax'] = self

    def create_module(self, name, attrs):
        f = open(os.path.join(self.__path__[0], name+'.py'), 'w')
        self._fake_module_paths.append(f.name)
        for name in attrs:
            f.write('%s = 42\n' % name)
        f.close()

    def cleanup(self):
        for path in self._fake_module_paths:
            os.unlink(path)
        del sys.modules['java']
        del sys.modules['javax']
    

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
