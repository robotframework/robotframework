#!/usr/bin/env python

"""ug2html.py -- Creates HTML version of Robot Framework User Guide

Usage:  ug2html.py [ cr(eate) | dist | zip ]

create .. Creates the user guide so that it has relative links to images,
          library docs, etc. Mainly used to test how changes look in HTML.

dist .... Creates the user guide under 'robotframework-userguide-<version>'
          directory and also copies all needed images and other link targets
          there. Also compiles library docs to ensure latest versions are
          included. The created output directory can thus be distributed
          independently.

zip ..... Uses 'dist' to create a stand-alone distribution and then packages
          it into 'robotframework-userguide-<version>.zip'

Version number to use is got automatically from 'src/robot/version.py' file
created by 'package.py'.
"""

import os
import sys
import shutil

# First part of this file is Pygments configuration and actual
# documentation generation follows it.
#

#
# Pygments configuration
# ----------------------
#
# This code is from 'external/rst-directive.py' file included in Pygments 0.9
# distribution. For more details see http://pygments.org/docs/rstdirective/
#
"""
    The Pygments MoinMoin Parser
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This fragment is a Docutils_ 0.4 directive that renders source code
    (to HTML only, currently) via Pygments.

    To use it, adjust the options below and copy the code into a module
    that you import on initialization.  The code then automatically
    registers a ``sourcecode`` directive that you can use instead of
    normal code blocks like this::

        .. sourcecode:: python

            My code goes here.

    If you want to have different code styles, e.g. one with line numbers
    and one without, add formatters with their names in the VARIANTS dict
    below.  You can invoke them instead of the DEFAULT one by using a
    directive option::

        .. sourcecode:: python
            :linenos:

            My code goes here.

    Look at the `directive documentation`_ to get all the gory details.

    .. _Docutils: http://docutils.sf.net/
    .. _directive documentation:
       http://docutils.sourceforge.net/docs/howto/rst-directives.html

    :copyright: 2007 by Georg Brandl.
    :license: BSD, see LICENSE for more details.
"""

# Options
# ~~~~~~~

# Set to True if you want inline CSS styles instead of classes
INLINESTYLES = False

from pygments.formatters import HtmlFormatter

# The default formatter
DEFAULT = HtmlFormatter(noclasses=INLINESTYLES)

# Add name -> formatter pairs for every variant you want to use
VARIANTS = {
    # 'linenos': HtmlFormatter(noclasses=INLINESTYLES, linenos=True),
}

from docutils import nodes
from docutils.parsers.rst import directives

from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer

def pygments_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    try:
        lexer = get_lexer_by_name(arguments[0])
    except ValueError:
        # no lexer found - use the text one instead of an exception
        lexer = TextLexer()
    # take an arbitrary option if more than one is given
    formatter = options and VARIANTS[options.keys()[0]] or DEFAULT
    # possibility to read the content from an external file
    filtered = [ line for line in content if line.strip() ]
    if len(filtered) == 1:
        path = filtered[0].replace('/', os.sep)
        if os.path.isfile(path):
            content = open(path).read().splitlines()
    parsed = highlight(u'\n'.join(content), lexer, formatter)
    return [nodes.raw('', parsed, format='html')]

pygments_directive.arguments = (1, 0, 1)
pygments_directive.content = 1
pygments_directive.options = dict([(key, directives.flag) for key in VARIANTS])

directives.register_directive('sourcecode', pygments_directive)


#
# Create the user guide using docutils
#
# This code is based on rst2html.py distributed with docutils
#

CURDIR = os.path.dirname(os.path.abspath(__file__))

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass


def create_userguide():
    from docutils.core import publish_cmdline

    print 'Creating user guide ...'
    version, version_file = _update_version()
    install_file = _copy_installation_instructions()

    description = 'HTML generator for Robot Framework User Guide.'
    arguments = ['--time',
                 '--stylesheet-path', ['src/userguide.css'],
                 'src/RobotFrameworkUserGuide.rst',
                 'RobotFrameworkUserGuide.html']
    os.chdir(CURDIR)
    publish_cmdline(writer_name='html', description=description, argv=arguments)
    os.unlink(version_file)
    os.unlink(install_file)
    ugpath = os.path.abspath(arguments[-1])
    print ugpath
    return ugpath, version


def _update_version():
    version = _get_version()
    print 'Version:', version
    with open(os.path.join(CURDIR, 'src', 'version.rst'), 'w') as vfile:
        vfile.write('.. |version| replace:: %s\n' % version)
    return version, vfile.name

def _get_version():
    namespace = {}
    execfile(os.path.join(CURDIR, '..', '..', 'src', 'robot', 'version.py'),
             namespace)
    return namespace['get_version']()

def _copy_installation_instructions():
    source = os.path.join(CURDIR, '..', '..', 'INSTALL.rst')
    target = os.path.join(CURDIR, 'src', 'GettingStarted', 'INSTALL.rst')
    include = True
    with open(source) as source_file:
        with open(target, 'w') as target_file:
            for line in source_file:
                if 'START USER GUIDE IGNORE' in line:
                    include = False
                if include:
                    target_file.write(line)
                if 'END USER GUIDE IGNORE' in line:
                    include = True
    return target


#
# Create user guide distribution directory
#
def create_distribution():
    import re
    from urlparse import urlparse

    dist = os.path.normpath(os.path.join(CURDIR, '..', '..', 'dist'))
    ugpath, version = create_userguide()  # we are in doc/userguide after this
    outdir = os.path.join(dist, 'robotframework-userguide-%s' % version)
    templates = os.path.join(outdir, 'templates')
    libraries = os.path.join(outdir, 'libraries')
    images = os.path.join(outdir, 'images')
    print 'Creating distribution directory ...'

    if os.path.exists(outdir):
        print 'Removing previous user guide distribution'
        shutil.rmtree(outdir)
    elif not os.path.exists(dist):
        os.mkdir(dist)

    print 'Recompiling library docs'
    sys.path.insert(0, os.path.join(CURDIR, '..', 'libraries'))
    import lib2html
    lib2html.create_all()

    for dirname in [outdir, templates, libraries, images]:
        print "Creating output directory '%s'" % dirname
        os.mkdir(dirname)

    def replace_links(res):
        if not res.group(5):
            return res.group(0)
        scheme, _, path, _, _, fragment = urlparse(res.group(5))
        if scheme or (fragment and not path):
            return res.group(0)
        replaced_link = '%s %s="%%s/%s"' % (res.group(1), res.group(4),
                                            os.path.basename(path))
        if path.startswith('../../templates'):
            copy(path, templates)
            replaced_link = replaced_link % 'templates'
        elif path.startswith('../libraries'):
            copy(path, libraries)
            replaced_link = replaced_link % 'libraries'
        elif path.startswith('src/'):
            copy(path, images)
            replaced_link = replaced_link % 'images'
        else:
            raise ValueError('Invalid link target: %s (context: %s)'
                             % (path, res.group(0)))
        print "Modified link '%s' -> '%s'" % (res.group(0), replaced_link)
        return replaced_link

    def copy(source, dest):
        print "Copying '%s' -> '%s'" % (source, dest)
        shutil.copy(source, dest)

    link_regexp = re.compile('''
(<(a|img)\s+.*?)
(\s+(href|src)="(.*?)"|>)
''', re.VERBOSE | re.DOTALL | re.IGNORECASE)

    with open(ugpath) as infile:
        content = link_regexp.sub(replace_links, infile.read())
    with open(os.path.join(outdir, os.path.basename(ugpath)), 'wb') as outfile:
        outfile.write(content)
    print os.path.abspath(outfile.name)
    return outdir

#
# Create a zip distribution package
#
def create_zip():
    ugdir = create_distribution()
    print 'Creating zip package ...'
    zip_path = zip_distribution(ugdir)
    print 'Removing distribution directory', ugdir
    shutil.rmtree(ugdir)
    print zip_path


def zip_distribution(dirpath):
    from zipfile import ZipFile, ZIP_DEFLATED

    zippath = os.path.normpath(dirpath) + '.zip'
    arcroot = os.path.dirname(dirpath)

    with ZipFile(zippath, 'w', compression=ZIP_DEFLATED) as zipfile:
        for root, _, files in os.walk(dirpath):
            for name in files:
                path = os.path.join(root, name)
                arcpath = os.path.relpath(path, arcroot)
                print "Adding '%s'" % arcpath
                zipfile.write(path, arcpath)

    return os.path.abspath(zippath)


if __name__ == '__main__':
    actions = { 'create': create_userguide, 'cr': create_userguide,
                'dist': create_distribution, 'zip': create_zip }
    try:
        actions[sys.argv[1]](*sys.argv[2:])
    except (KeyError, IndexError, TypeError):
        print __doc__
