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

"""Implements `libdoc` tool.

For programmatic entry point, see :mod:`robot.libdoc`.

This package is considered stable.
"""

from .builder import DocumentationBuilder
from .consoleviewer import ConsoleViewer


def LibraryDocumentation(library_or_resource, name=None, version=None):
    builder = DocumentationBuilder(library_or_resource)
    libdoc = builder.build(library_or_resource)
    if name:
        libdoc.name = name
    if version:
        libdoc.version = version
    return libdoc
