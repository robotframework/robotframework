#!/usr/bin/env python

"""ug2html.py -- Creates HTML version of Robot Framework User Guide

Synopsis:
ug2html.py [ cr(eate) | dist ]

Description:
With 'create' as argument, user guide will be generated. This userguide will 
have relative links that work only from version control or with full source 
distribution.

With 'dist' as argument, 'rfug' directory is created and all images and link 
targets are copied under it. This way the created output directory may be 
compressed and the user guide distributed independently.
"""


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

import os

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
    filtered = [ line for line in content if line ]
    if len(filtered) and os.path.isfile(filtered[0]):
        content = open(content[0]).read().splitlines() # Read source code from a file
    parsed = highlight(u'\n'.join(content), lexer, formatter)
    return [nodes.raw('', parsed, format='html')]

pygments_directive.arguments = (1, 0, 1)
pygments_directive.content = 1
pygments_directive.options = dict([(key, directives.flag) for key in VARIANTS])

directives.register_directive('sourcecode', pygments_directive)

#
# Create outputdir and move images and library documentation there
#


def distribute_userguide():
    import shutil
    import re
    from urlparse import urlparse

    create_userguide()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    outdir = "rfug"
    toolsdir = os.path.join(outdir, 'tools')
    librariesdir = os.path.join(outdir, 'libraries')
    imagesdir = os.path.join(outdir, 'images')

    if os.path.exists(outdir):
        print 'Removing previous user guide distribution'
        shutil.rmtree(outdir)
    
    for dirname in [outdir, toolsdir, librariesdir, imagesdir]:
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
        if path.startswith('../../tools'):
            copy(path, toolsdir)
            copy_tool_images(path)
            replaced_link = replaced_link % 'tools'
        elif path.startswith('../libraries'):
            copy(path, librariesdir)
            replaced_link = replaced_link % 'libraries'
        elif path.startswith('src/'):
            copy(path, imagesdir)
            replaced_link = replaced_link % 'images'
        else:
            raise ValueError('Invalid link target: %s' % path)
        print "Modified link '%s' -> '%s'" % (res.group(0), replaced_link)
        return replaced_link

    def copy(source, dest):
        print "Copying '%s' -> '%s'" % (source, dest)
        shutil.copy(source, dest)

    def copy_tool_images(path):
        indir = os.path.dirname(path)
        for line in open(os.path.splitext(path)[0]+'.txt').readlines():
            if line.startswith('.. figure::'):
                copy(os.path.join(indir, line.strip().split()[-1]), toolsdir)

    link_regexp = re.compile('''
(<(a|img)\s+.*?)
(\s+(href|src)="(.*?)"|>)
''', re.VERBOSE | re.DOTALL | re.IGNORECASE)

    content = open('RobotFrameworkUserGuide.html').read()
    content = link_regexp.sub(replace_links, content)
    outfile = open(os.path.join(outdir, 'RobotFrameworkUserGuide.html'), 'wb')
    outfile.write(content)
    outfile.close()

#
# Creating the documentation
#
# This code is based on rst2html.py distributed with docutils
#
def create_userguide():
    try:
        import locale
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass

    from docutils.core import publish_cmdline

    description = 'HTML generator for Robot Framework User Guide.'
    arguments = '''
--time
--stylesheet-path=src/userguide.css
src/RobotFrameworkUserGuide.txt
RobotFrameworkUserGuide.html
'''.split('\n')[1:-1] 

    publish_cmdline(writer_name='html', description=description, argv=arguments)

    print os.path.abspath(arguments[-1])

if __name__ == '__main__':
    import sys
    actions = { 'create': create_userguide, 'cr': create_userguide,
                'dist': distribute_userguide }
    try:
        actions[sys.argv[1]]()
    except (KeyError, IndexError):
        print __doc__

