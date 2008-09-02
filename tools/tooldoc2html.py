#!/usr/bin/env python

# tooldoc2html.py -- Creates HTML version of given tool documentation
#
# First part of this file is Pygments configuration and actual
# documentation generation follows it.


#
# Pygments configuration
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
    if len(filtered)==1 and os.path.isfile(filtered[0]):
        content = open(content[0]).read().splitlines()
    parsed = highlight(u'\n'.join(content), lexer, formatter)
    return [nodes.raw('', parsed, format='html')]

pygments_directive.arguments = (1, 0, 1)
pygments_directive.content = 1
pygments_directive.options = dict([(key, directives.flag) for key in VARIANTS])

directives.register_directive('sourcecode', pygments_directive)

#
# Creating the documentation
#
# This code is based on rst2html.py distributed with docutils
#

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

import sys
from docutils.core import publish_cmdline


def create_tooldoc(tool_name):
    description = 'HTML generator for Robot Framework Tool Documentation.'
    stylesheet_path = os.path.join(BASEDIR, '..', 'doc', 'userguide', 'src', 
                                   'userguide.css')
    base_path = os.path.join(BASEDIR, tool_name, 'doc', tool_name)
    arguments = [ '--time', '--stylesheet-path=%s' % stylesheet_path,
                  base_path + '.txt', base_path + '.html' ]

    publish_cmdline(writer_name='html', description=description, argv=arguments)
    print os.path.abspath(arguments[-1])


BASEDIR = os.path.dirname(os.path.abspath(__file__))
VALID_TOOLS = [ name for name in os.listdir(BASEDIR) if '.' not in name ]


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1].lower() not in VALID_TOOLS + ['all']:
        print "Usage:  %s toolname | all\n" % (os.path.basename(sys.argv[0]))
        print "Tools:"
        for tool in sorted(VALID_TOOLS):
            print '  %s' % tool
        sys.exit(1)
    tool = sys.argv[1].lower()
    if tool == 'all':
        for name in VALID_TOOLS:
            create_tooldoc(name)
    else:
        create_tooldoc(tool)
