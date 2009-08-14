#!/usr/bin/env python

"""pt2html.py -- Creates HTML version of Python Tutorial

Usage:  pt2html.py
"""

import sys
import os
import shutil
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'userguide'))
import ug2html  # This also initializes docutils and pygments


def create_tutorial():
    from docutils.core import publish_cmdline

    print 'Creating Python Tutorial ...'
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    description = 'Python Tutorial for Robot Framework Library Developers'
    arguments = '''
--time
--stylesheet-path=../userguide/src/userguide.css
PythonTutorial.rst
PythonTutorial.html
'''.split('\n')[1:-1] 
    publish_cmdline(writer_name='html', description=description, argv=arguments)
    path = arguments[-1]
    print os.path.abspath(path)
    return path


if __name__ == '__main__':
    create_tutorial()
