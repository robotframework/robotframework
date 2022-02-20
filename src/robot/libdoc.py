#!/usr/bin/env python

#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Module implementing the command line entry point for the Libdoc tool.

This module can be executed from the command line using the following
approaches::

    python -m robot.libdoc
    python path/to/robot/libdoc.py

Instead of ``python`` it is possible to use also other Python interpreters.

This module also provides :func:`libdoc` and :func:`libdoc_cli` functions
that can be used programmatically. Other code is for internal usage.

Libdoc itself is implemented in the :mod:`~robot.libdocpkg` package.
"""

import sys
import os

# Allows running as a script. __name__ check needed with multiprocessing:
# https://github.com/robotframework/robotframework/issues/1137
if 'robot' not in sys.modules and __name__ == '__main__':
    import pythonpathsetter

from robot.utils import Application, seq2str
from robot.errors import DataError
from robot.libdocpkg import LibraryDocumentation, ConsoleViewer


USAGE = """Libdoc -- Robot Framework library documentation generator

Version:  <VERSION>

Usage:  libdoc [options] library_or_resource output_file
   or:  libdoc [options] library_or_resource list|show|version [names]

Libdoc can generate documentation for Robot Framework libraries and resource
files. It can generate HTML documentation for humans as well as machine
readable spec files in XML and JSON formats. Libdoc also has few special
commands to show library or resource information on the console.

Libdoc supports all library and resource types and also earlier generated XML
and JSON specs can be used as input. If a library needs arguments, they must be
given as part of the library name and separated by two colons, for example,
like `LibraryName::arg1::arg2`.

The easiest way to run Libdoc is using the `libdoc` command created as part of
the normal installation. Alternatively it is possible to execute the
`robot.libdoc` module directly like `python -m robot.libdoc`, where `python`
can be replaced with any supported Python interpreter. Yet another alternative
is running the module as a script like `python path/to/robot/libdoc.py`.

The separate `libdoc` command and the support for JSON spec files are new in
Robot Framework 4.0.

Options
=======

 -f --format HTML|XML|JSON|LIBSPEC
                          Specifies whether to generate an HTML output for
                          humans or a machine readable spec file in XML or JSON
                          format. The `libspec` format means XML spec with
                          documentations converted to HTML. The default format
                          is got from the output file extension.
 -s --specdocformat RAW|HTML
                          Specifies the documentation format used with XML and
                          JSON spec files. `raw` means preserving the original
                          documentation format and `html` means converting
                          documentation to HTML. The default is `raw` with XML
                          spec files and `html` with JSON specs and when using
                          the special `libspec` format. New in RF 4.0.
 -F --docformat ROBOT|HTML|TEXT|REST
                          Specifies the source documentation format. Possible
                          values are Robot Framework's documentation format,
                          HTML, plain text, and reStructuredText. The default
                          value can be specified in library source code and
                          the initial default value is `ROBOT`.
 -n --name name           Sets the name of the documented library or resource.
 -v --version version     Sets the version of the documented library or
                          resource.
    --quiet               Do not print the path of the generated output file
                          to the console. New in RF 4.0.
 -P --pythonpath path *   Additional locations where to search for libraries
                          and resources.
 -h -? --help             Print this help.

Creating documentation
======================

When creating documentation in HTML, XML or JSON format, the output file must
be specified as the second argument after the library or resource name or path.

Output format is got automatically from the output file extension. In addition
to `*.html`, `*.xml` and `*.json` extensions, it is possible to use the special
`*.libspec` extensions which means XML spec with actual library and keyword
documentation converted to HTML. The format can also be set explicitly using
the `--format` option.

Examples:

  libdoc src/MyLibrary.py doc/MyLibrary.html
  libdoc doc/MyLibrary.json doc/MyLibrary.html
  libdoc --name MyLibrary Remote::10.0.0.42:8270 MyLibrary.xml
  libdoc MyLibrary MyLibrary.libspec

Viewing information on console
==============================

Libdoc has three special commands to show information on the console. These
commands are used instead of the name of the output file, and they can also
take additional arguments.

list:    List names of the keywords the library/resource contains. Can be
         limited to show only certain keywords by passing optional patterns as
         arguments. Keyword is listed if its name contains any given pattern.
show:    Show library/resource documentation. Can be limited to show only
         certain keywords by passing names as arguments. Keyword is shown if
         its name matches any given name. Special argument `intro` will show
         the library introduction and importing sections.
version: Show library version

Optional patterns given to `list` and `show` are case and space insensitive.
Both also accept `*` and `?` as wildcards.

Examples:

  libdoc Dialogs list
  libdoc SeleniumLibrary list browser
  libdoc Remote::10.0.0.42:8270 show
  libdoc Dialogs show PauseExecution execute*
  libdoc SeleniumLibrary show intro
  libdoc SeleniumLibrary version

Alternative execution
=====================

Libdoc works with all interpreters supported by Robot Framework.
 In the examples above Libdoc is executed as an
installed module, but it can also be executed as a script like
`python path/robot/libdoc.py`.

For more information about Libdoc and other built-in tools, see
http://robotframework.org/robotframework/#built-in-tools.
"""


class LibDoc(Application):

    def __init__(self):
        Application.__init__(self, USAGE, arg_limits=(2,), auto_version=False)

    def validate(self, options, arguments):
        if ConsoleViewer.handles(arguments[1]):
            ConsoleViewer.validate_command(arguments[1], arguments[2:])
            return options, arguments
        if len(arguments) > 2:
            raise DataError('Only two arguments allowed when writing output.')
        return options, arguments

    def main(self, args, name='', version='', format=None, docformat=None,
             specdocformat=None, pythonpath=None, quiet=False):
        if pythonpath:
            sys.path = pythonpath + sys.path
        lib_or_res, output = args[:2]
        docformat = self._get_docformat(docformat)
        libdoc = LibraryDocumentation(lib_or_res, name, version, docformat)
        if ConsoleViewer.handles(output):
            ConsoleViewer(libdoc).view(output, *args[2:])
            return
        format, specdocformat \
            = self._get_format_and_specdocformat(format, specdocformat, output)
        if (format == 'HTML'
                or specdocformat == 'HTML'
                or format in ('JSON', 'LIBSPEC') and specdocformat != 'RAW'):
            libdoc.convert_docs_to_html()
        libdoc.save(output, format)
        if not quiet:
            self.console(os.path.abspath(output))

    def _get_docformat(self, docformat):
        return self._validate_format('Doc format', docformat,
                                     ['ROBOT', 'TEXT', 'HTML', 'REST'])

    def _get_format_and_specdocformat(self, format, specdocformat, output):
        extension = os.path.splitext(output)[1][1:]
        format = self._validate_format('Format', format or extension,
                                       ['HTML', 'XML', 'JSON', 'LIBSPEC'])
        specdocformat = self._validate_format('Spec doc format', specdocformat,
                                              ['RAW', 'HTML'])
        if format == 'HTML' and specdocformat:
            raise DataError("The --specdocformat option is not applicable with "
                            "HTML outputs.")
        return format, specdocformat

    def _validate_format(self, type, format, valid):
        if format is None:
            return None
        format = format.upper()
        if format not in valid:
            raise DataError("%s must be %s, got '%s'."
                            % (type, seq2str(valid, lastsep=' or '), format))
        return format


def libdoc_cli(arguments=None, exit=True):
    """Executes Libdoc similarly as from the command line.

    :param arguments: Command line options and arguments as a list of strings.
        Starting from RF 4.0, defaults to ``sys.argv[1:]`` if not given.
    :param exit: If ``True``, call ``sys.exit`` automatically. New in RF 4.0.

    The :func:`libdoc` function may work better in programmatic usage.

    Example::

        from robot.libdoc import libdoc_cli

        libdoc_cli(['--version', '1.0', 'MyLibrary.py', 'MyLibrary.html'])
    """
    if arguments is None:
        arguments = sys.argv[1:]
    LibDoc().execute_cli(arguments, exit=exit)


def libdoc(library_or_resource, outfile, name='', version='', format=None,
           docformat=None, specdocformat=None, quiet=False):
    """Executes Libdoc.

    :param library_or_resource: Name or path of the library or resource
        file to be documented.
    :param outfile: Path path to the file where to write outputs.
    :param name: Custom name to give to the documented library or resource.
    :param version: Version to give to the documented library or resource.
    :param format: Specifies whether to generate HTML, XML or JSON output.
        If this options is not used, the format is got from the extension of
        the output file. Possible values are ``'HTML'``, ``'XML'``, ``'JSON'``
        and ``'LIBSPEC'``.
    :param docformat: Documentation source format. Possible values are
        ``'ROBOT'``, ``'reST'``, ``'HTML'`` and ``'TEXT'``. The default value
        can be specified in library source code and the initial default
        is ``'ROBOT'``.
    :param specdocformat: Specifies whether the keyword documentation in spec
        files is converted to HTML regardless of the original documentation
        format. Possible values are ``'HTML'`` (convert to HTML) and ``'RAW'``
        (use original format). The default depends on the output format.
        New in Robot Framework 4.0.
    :param quiet: When true, the path of the generated output file is not
        printed the console. New in Robot Framework 4.0.

    Arguments have same semantics as Libdoc command line options with same names.
    Run ``libdoc --help`` or consult the Libdoc section in the Robot Framework
    User Guide for more details.

    Example::

        from robot.libdoc import libdoc

        libdoc('MyLibrary.py', 'MyLibrary.html', version='1.0')
    """
    return LibDoc().execute(
        library_or_resource, outfile, name=name, version=version, format=format,
        docformat=docformat, specdocformat=specdocformat, quiet=quiet
    )


if __name__ == '__main__':
    libdoc_cli(sys.argv[1:])
