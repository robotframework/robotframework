#!/usr/bin/env python

"""qs2html.py -- Creates HTML version of Robot Framework Quick Start Guide

Usage:  qs2html.py [ cr(eate) | dist | zip ]

create .. Creates the quick start guide in HTML format.

dist .... Creates the quick start guide and copies it and all its dependencies 
	  under directory named robotframework-quickstart

zip ..... Uses 'dist' to create the quick start guide under a directory and then
	  packages the directory into 'robotframework-quickstart.zip'

"""

import sys
import os
import shutil

sys.path.insert(0, os.path.join('..', 'userguide'))
import ug2html  # This initializes docutils and pygments


def create_quickstart():
    from docutils.core import publish_cmdline

    print 'Creating quick start guide ...'
    qsdir = os.path.dirname(os.path.abspath(__file__))
    description = 'Quick Start Guide for Robot Framework'
    arguments = '''
--time
--stylesheet-path=../userguide/src/userguide.css
quickstart.txt
quickstart.html
'''.split('\n')[1:-1] 

    os.chdir(qsdir)
    publish_cmdline(writer_name='html', description=description, argv=arguments)
    qspath = os.path.abspath(arguments[-1])
    print qspath
    return qspath


def create_distribution():
    qspath = create_quickstart() # we are in doc/quickstart after this
    outdir = 'robotframework-quickstart'
    files = { '.': [qspath],
              'sut': ['login.py', 'test_login.py'],
              'testlibs': ['LoginLibrary.py'] }

    print 'Creating distribution directory ...'
    if os.path.exists(outdir):
        print 'Removing previous distribution'
        shutil.rmtree(outdir)
    os.mkdir(outdir)
    for dirname, files in files.items():
        dirpath = os.path.join(outdir, dirname)
        if not os.path.exists(dirpath):
            print "Creating output directory '%s'" % dirpath
            os.mkdir(dirpath)
        for name in files:
            source = os.path.join(dirname, name)
            print "Copying '%s' -> '%s'" % (source, dirpath)
            shutil.copy(source, dirpath)
    return outdir     


def create_zip():
    qsdir = create_distribution()
    ug2html.zip_distribution(qsdir)


if __name__ == '__main__':
    actions = { 'create': create_quickstart, 'cr': create_quickstart,
                'dist': create_distribution, 'zip': create_zip }
    try:
        actions[sys.argv[1]](*sys.argv[2:])
    except (KeyError, IndexError, TypeError):
        print __doc__

