#! /usr/bin/env python

"""generate.py -- Generate Robot Framework API documentation

usage: generate.py

This script updates the package index files using `sphinx-apidoc`, cds into
doc/api and calls `make html`.
"""

import sys
import os
from os.path import abspath, dirname, join
from subprocess import call

BUILD_DIR = abspath(dirname(__file__))
ROBOT_DIR = join(BUILD_DIR, '..', '..', 'src', 'robot')


def generate():
    update()
    orig_dir = abspath(os.curdir)
    os.chdir(BUILD_DIR)
    rc = call(['make', 'html'], shell=os.name=='nt')
    os.chdir(orig_dir)
    print abspath(join(BUILD_DIR, '_build', 'html', 'index.html'))
    return rc

def update():
    call(['sphinx-apidoc', '--output-dir', BUILD_DIR, '--force' , '--no-toc',
          '--maxdepth', '2', ROBOT_DIR])


if __name__ == '__main__':
    if sys.argv[1:]:
        print __doc__
        sys.exit(1)
    try:
        import sphinx as _
    except ImportError:
        sys.exit('Generating API docs requires Sphinx')
    else:
        sys.exit(generate())
