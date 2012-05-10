#! /usr/bin/env python

"""generate.py -- Generate Robot Framework API documentation

usage: generate.py

This script creates API documentation from both Python and Java source code
included in `src/python and `src/java`, respectively. Python autodocs are
created in `doc/api/autodoc` and Javadocs in `doc/api/_static/javadoc`.

API documentation entry point is create using Sphinx's `make html`.

Sphinx, sphinx-apidoc and javadoc commands need to be in $PATH.
"""

import sys
import os
import shutil
from os.path import abspath, dirname, join
from subprocess import call

BUILD_DIR = abspath(dirname(__file__))
AUTODOC_DIR = join(BUILD_DIR, 'autodoc')
ROOT = join(BUILD_DIR, '..', '..')
ROBOT_DIR = join(ROOT, 'src', 'robot')
JAVA_SRC = join(ROOT, 'src', 'java')
JAVA_TARGET = join(BUILD_DIR, '_static', 'javadoc')


def generate():
    clean()
    update()
    create_javadoc()
    orig_dir = abspath(os.curdir)
    os.chdir(BUILD_DIR)
    rc = call(['make', 'html'], shell=os.name == 'nt')
    os.chdir(orig_dir)
    print abspath(join(BUILD_DIR, '_build', 'html', 'index.html'))
    return rc


def clean():
    for dirname in AUTODOC_DIR, JAVA_TARGET:
        if os.path.exists(dirname):
            print 'Cleaning', dirname
            shutil.rmtree(dirname)


def update():
    print 'Creating autodoc'
    call(['sphinx-apidoc', '--output-dir', AUTODOC_DIR, '--force', '--no-toc',
          '--maxdepth', '2', ROBOT_DIR])


def create_javadoc():
    print 'Creating javadoc'
    call(['javadoc', '-sourcepath', JAVA_SRC, '-d', JAVA_TARGET,
          '-notimestamp', 'org.robotframework'])


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
