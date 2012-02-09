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

import sys
import os

from robot.errors import DataError
from robot.parsing import VALID_EXTENSIONS

if sys.platform.startswith('java'):
    from .javalibdocbuilder import JavaDocBuilder
else:
    def JavaDocBuilder():
        raise DataError('Documenting Java test libraries requires Jython.')
from .librarydocoutput import LibraryDocOutput
from .robotlibdoc import LibraryDocBuilder, ResourceDocBuilder
from .xmlwriter import LibdocXmlWriter
from .libdochtmlwriter import LibdocHtmlWriter


def LibraryDoc(library_or_resource, arguments=None, name=None, version=None):
    extension = os.path.splitext(library_or_resource)[1][1:].lower()
    if extension == 'java':
        libdoc = JavaDocBuilder().build(library_or_resource)
    elif extension in VALID_EXTENSIONS:
        libdoc = ResourceDocBuilder().build(library_or_resource)
    else:
        libdoc = LibraryDocBuilder().build(library_or_resource, arguments)
    if name:
        libdoc.name = name
    if version:
        libdoc.version = version
    return libdoc


def LibraryDocWriter(format=None, title=None, style=None):
    format = (format or 'HTML').upper()
    if format == 'HTML':
        return LibdocHtmlWriter(title, style)
    if format == 'XML':
        return LibdocXmlWriter()
    raise DataError("Format must be either 'HTML' or 'XML', got '%s'." % format)
