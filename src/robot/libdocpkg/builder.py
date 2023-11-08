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

import os
from pathlib import Path

from robot.errors import DataError
from robot.utils import get_error_message

from .jsonbuilder import JsonDocBuilder
from .robotbuilder import LibraryDocBuilder, ResourceDocBuilder, SuiteDocBuilder
from .xmlbuilder import XmlDocBuilder


RESOURCE_EXTENSIONS = ('resource', 'robot', 'txt', 'tsv', 'rst', 'rest')
XML_EXTENSIONS = ('xml', 'libspec')


def LibraryDocumentation(library_or_resource, name=None, version=None, doc_format=None):
    """Generate keyword documentation for the given library, resource or suite file.

    :param library_or_resource:
        Name or path of the library, or path of a resource or a suite file.
    :param name:
        Set name with the given value.
    :param version:
        Set version to the given value.
    :param doc_format:
        Set documentation format to the given value.
    :return:
        :class:`~.model.LibraryDoc` instance.

    This factory method is the recommended API to generate keyword documentation
    programmatically. It should be imported via the :mod:`robot.libdoc` module.

    Example::

        from robot.libdoc import LibraryDocumentation

        lib = LibraryDocumentation('OperatingSystem')
        print(lib.name, lib.version)
        for kw in lib.keywords:
            print(kw.name)
    """
    libdoc = DocumentationBuilder().build(library_or_resource)
    if name:
        libdoc.name = name
    if version:
        libdoc.version = version
    if doc_format:
        libdoc.doc_format = doc_format
    return libdoc


class DocumentationBuilder:
    """Keyword documentation builder.

    This is not part of Libdoc's public API. Use :func:`LibraryDocumentation`
    instead.
    """

    def build(self, source):
        # Source can contain arguments separated with `::` so we cannot convert
        # it to Path and instead need to make sure it's a string. It would be
        # better to separate arguments earlier, or latest here, and use Path.
        if isinstance(source, Path):
            source = str(source)
        builder = self._get_builder(source)
        return self._build(builder, source)

    def _get_builder(self, source):
        if os.path.exists(source):
            extension = self._get_extension(source)
            if extension == 'resource':
                return ResourceDocBuilder()
            if extension in RESOURCE_EXTENSIONS:
                return SuiteDocBuilder()
            if extension in XML_EXTENSIONS:
                return XmlDocBuilder()
            if extension == 'json':
                return JsonDocBuilder()
        return LibraryDocBuilder()

    def _get_extension(self, source):
        path, *args = source.split('::')
        return os.path.splitext(path)[1][1:].lower()

    def _build(self, builder, source):
        try:
            return builder.build(source)
        except DataError:
            # Possible resource file in PYTHONPATH. Something like `xxx.resource` that
            # did not exist has been considered to be a library earlier, now we try to
            # parse it as a resource file.
            if (isinstance(builder, LibraryDocBuilder)
                    and not os.path.exists(source)
                    and self._get_extension(source) in RESOURCE_EXTENSIONS):
                return self._build(ResourceDocBuilder(), source)
            # Resource file with other extension than '.resource' parsed as a suite file.
            if isinstance(builder, SuiteDocBuilder):
                return self._build(ResourceDocBuilder(), source)
            raise
        except Exception:
            raise DataError(f"Building library '{source}' failed: {get_error_message()}")
