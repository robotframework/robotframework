#!/usr/bin/env python

"""package.py --  Create documentation or package Robot Framework C example

Usage:  qs2html.py [ doc | dist ]

doc ... Creates the HTML version of the documentation.

dist .. Packages code, tests and documentation in 'robotframework-c-example-<date>'.zip
"""

import sys
import os
import shutil
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'userguide'))
import ug2html  # This also initializes docutils and pygments


def create_doc():
    from docutils.core import publish_cmdline

    print 'Creating documentation ...'
    description = 'Documentation for Robot Framework C-library example'
    arguments = '''
--time
--stylesheet-path=../../userguide/src/userguide.css
README
README.html
'''.split('\n')[1:-1]

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    publish_cmdline(writer_name='html', description=description, argv=arguments)
    outpath = arguments[-1]
    print os.path.abspath(outpath)
    return outpath


def create_distribution():
    outpath = create_doc()  # we are in doc/examples/c_example after this
    outdir = 'robotframework-c-example-%d%02d%02d' % time.localtime()[:3]
    files = ['login.c', 'LoginLibrary.py', 'LoginTests.tsv', 'Makefile', 'README', 'README.html']
    print 'Creating distribution directory ...'
    if os.path.exists(outdir):
        print 'Removing previous distribution'
        shutil.rmtree(outdir)
    os.mkdir(outdir)
    for name in files:
        print "Copying '%s' -> '%s'" % (name, outdir)
        shutil.copy(name, outdir)
    ug2html.zip_distribution(outdir)


if __name__ == '__main__':
    actions = { 'doc': create_doc,
                'dist': create_distribution }
    try:
        actions[sys.argv[1]](*sys.argv[2:])
    except (KeyError, IndexError, TypeError):
        print __doc__

