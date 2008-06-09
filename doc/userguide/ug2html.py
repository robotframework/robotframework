#!/usr/bin/env python

# ug2html.py -- Creates HTML version of Robot Framework User Guide
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
# Create outputdir and move images and library documentation there
#
import glob
import shutil


os.chdir(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = "rfug"

if os.path.exists(OUTDIR):
    shutil.rmtree(OUTDIR)
os.mkdir(OUTDIR)

def copy_figures(filename):
    dirname = os.path.dirname(filename)
    images = [ line[12:] for line in open(filename).read().splitlines() if line.startswith(".. figure") ]
    for image in images:
        shutil.copy(os.path.join(dirname, image), OUTDIR)

for filename in glob.glob('src/*/*.txt') + glob.glob('../../tools/*/doc/*.txt'):
    copy_figures(filename)


for doc in glob.glob('../libraries/*.html') + glob.glob('../../tools/*/doc/*.html'):
    shutil.copy(doc, OUTDIR)

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

from docutils.core import publish_cmdline


description = 'HTML generator for Robot Framework User Guide.'
arguments = ('''
--time
--stylesheet-path=src/userguide.css
src/RobotFrameworkUserGuide.txt
%s/RobotFrameworkUserGuide.html
''' % OUTDIR).split('\n')[1:-1] 


publish_cmdline(writer_name='html', description=description, argv=arguments)

print os.path.abspath(arguments[-1])

