#!/usr/bin/env python

#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

USAGE = """robot.libdoc -- Robot Framework library documentation generator

Version:  <VERSION>

Usage:  libdoc.py [options] library_or_resource output_file

This tool can generate keyword documentation in HTML and XML formats. The
former is suitable for humans and the latter for RIDE and other tools.

Documentation can be generated for both test libraries and resource files.
All library and resource file types are supported, and also documentation
generated earlier in XML format can be used as input.

Options
=======

 -f --format HTML|XML     Specifies whether to generate HTML or XML output.
                          If this options is not used, the format is got
                          from the extension of the output file.
 -n --name newname        Sets the name of the documented library or resource.
 -v --version newversion  Sets the version of the documented library or
                          resource.
 -a --argument value *    Possible argument(s) that the documented library
                          needs for initialization.
 -P --pythonpath path *   Additional path(s) to insert into PYTHONPATH.
 -E --escape what:with *  Escapes characters which are problematic in console.
                          'what' is the name of the character to escape and
                          'with' is the string to escape it with.
                          <-------------------ESCAPES------------------------>
 -h -? --help             Print this help.

Examples
========

  python -m robot.libdoc src/MyLib.py doc/MyLib.html
  python -m robot.libdoc BuiltIn spec.xml
  jython -m robot.libdoc  MyJavaLibrary.java MyJavaLibrary.html
  python -m robot.libdoc --format xml test/resource.html myoutfile

Alternative execution
=====================

Libdoc works with all interpretes supported by Robot Framework (Python,
Jython and IronPython). In the examples above libdoc is executed as an
installed module, but it can also be executed as a script like
`python path/robot/libdoc.py`.

For more information see the Robot Framework user guide at
http://code.google.com/p/robotframework/wiki/UserGuide
"""

import sys
import os

if 'robot' not in sys.modules:
    import pythonpathsetter   # running libdoc.py as script

from robot.utils import Application
from robot.errors import DataError
from robot.libdocpkg import LibraryDocumentation, ConsoleViewer


class LibDoc(Application):

    def __init__(self):
        Application.__init__(self, USAGE, arg_limits=(2,), auto_version=False)

    def validate(self, options, arguments):
        if len(arguments) > 2 and not ConsoleViewer.handles(arguments[1]):
            raise DataError('Only two arguments allowed when writing output.')
        return options, arguments

    def main(self, args, argument=None, name='', version='', format=None):
        lib_or_res, output = args[:2]
        libdoc = LibraryDocumentation(lib_or_res, argument, name, version)
        if ConsoleViewer.handles(output):
            ConsoleViewer(libdoc).view(output, *args[2:])
        else:
            libdoc.save(output, self._get_format(format, output))
            self.console(os.path.abspath(output))

    def _get_format(self, format, output):
        format = (format if format else os.path.splitext(output)[1][1:]).upper()
        if format in ['HTML', 'XML']:
            return format
        raise DataError("Format must be either 'HTML' or 'XML', got '%s'." % format)


def libdoc_cli(args):
    """Executes libdoc similarly as from the command line.

    :param args: command line arguments as a list of strings.

    Example:
        libdoc_cli(['--name', 'Something', 'MyLibrary.py', 'doc.html'])
    """
    LibDoc().execute_cli(args)

def libdoc(library_or_resource, output, arguments=None, name='', version='',
           format=None):
    """Executes libdoc.

    Arguments are same as command line options to libdoc.py.

    Example:
        libdoc('MyLibrary.py', 'MyLibrary.html', arguments=['1st', '2nd'])
    """
    LibDoc().execute(library_or_resource, output, argument=arguments,
                     name=name, version=version, format=format)


if __name__ == '__main__':
    libdoc_cli(sys.argv[1:])
