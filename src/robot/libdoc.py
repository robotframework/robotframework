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

USAGE = """Robot Framework Library and Resource File Documentation Generator

Version:  <VERSION>

Usage:  libdoc.py [options] library_or_resource

This script can generate keyword documentation in HTML and XML formats. The
former is suitable for humans and the latter for RIDE and other tools.

Documentation can be generated for both test libraries and resource files.
All library and resource file types are supported, and also documentation
generated earlier in XML format can be used as input.

Options
=======

 -a --argument value *    Possible argument(s) that a library needs.
 -f --format HTML|XML     Specifies whether to generate HTML or XML output.
                          If this options is not used, the format is got
                          from the extension of output, if given. Otherwise
                          the default is HTML.
 -o --output path         File to write the generated documentation to. If
                          not given, documentation if written to the standard
                          output.
 -n --name newname        Sets the name of the documented library or resource.
 -v --version newversion  Sets the version of the documented library or
                          resource.
 -P --pythonpath path *   Additional path(s) to insert into PYTHONPATH.
 -E --escape what:with *  Escapes characters which are problematic in console.
                          'what' is the name of the character to escape and
                          'with' is the string to escape it with.
                          <-------------------ESCAPES------------------------>
 -h -? --help             Print this help.

Examples:
  python -m robot.libdoc MyLibrary.py
  python -m robot.libdoc --output spec.xml myresource.txt
  python libdoc.py --python mylibdir --format xml MyLibrary

For more information see the Robot Framework user guide at
http://code.google.com/p/robotframework/wiki/UserGuide
"""

import sys
import os

if 'robot' not in sys.modules:
    import pythonpathsetter   # running libdoc.py as script

from robot.utils import Application
from robot.libdocpkg import LibraryDocumentation


class LibDoc(Application):

    def __init__(self):
        Application.__init__(self, USAGE, arg_limits=1, auto_version=False)

    def main(self, library_or_resource, argument=None, name='', version='',
             format='HTML', output=None):
        libdoc = LibraryDocumentation(library_or_resource[0], argument,
                                      name, version)
        libdoc.save(output, self._get_format(format, output))

    def _get_format(self, format, output):
        if format:
            return format
        if output:
            return os.path.splitext(output)[1][1:]
        return 'HTML'


def libdoc_cli(args):
    LibDoc().execute_cli(args)

def libdoc(library_or_resource, arguments=None, name='', version='',
           format='HTML', output=None):
    LibDoc().execute(library_or_resource, argument=arguments, name=name,
                     version=version, format=format, output=output)


if __name__ == '__main__':
    libdoc_cli(sys.argv[1:])
