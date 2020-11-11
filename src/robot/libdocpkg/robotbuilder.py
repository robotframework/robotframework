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
import sys
import re

from robot.errors import DataError
from robot.running import (TestLibrary, UserLibrary, UserErrorHandler,
                           ResourceFileBuilder)
from robot.utils import split_tags_from_doc, unescape, is_string
from robot.variables import VariableIterator, search_variable

from .model import LibraryDoc, KeywordDoc


class LibraryDocBuilder(object):
    _argument_separator = '::'

    def build(self, library):
        name, args = self._split_library_name_and_args(library)
        lib = TestLibrary(name, args)
        libdoc = LibraryDoc(name=lib.name,
                            doc=self._get_doc(lib),
                            version=lib.version,
                            scope=str(lib.scope),
                            doc_format=lib.doc_format,
                            source=lib.source,
                            lineno=lib.lineno)
        libdoc.inits = self._get_initializers(lib)
        libdoc.keywords = KeywordDocBuilder().build_keywords(lib)
        return libdoc

    def _split_library_name_and_args(self, library):
        args = library.split(self._argument_separator)
        name = args.pop(0)
        return self._normalize_library_path(name), args

    def _normalize_library_path(self, library):
        path = library.replace('/', os.sep)
        if os.path.exists(path):
            return os.path.abspath(path)
        return library

    def _get_doc(self, lib):
        return lib.doc or "Documentation for library ``%s``." % lib.name

    def _get_initializers(self, lib):
        if lib.init.arguments.maxargs:
            return [KeywordDocBuilder().build_keyword(lib.init)]
        return []


class ResourceDocBuilder(object):

    def build(self, path):
        res = self._import_resource(path)
        libdoc = LibraryDoc(name=res.name,
                            doc=self._get_doc(res),
                            type='RESOURCE',
                            scope='GLOBAL',
                            source=res.source,
                            lineno=1)
        libdoc.keywords = KeywordDocBuilder(resource=True).build_keywords(res)
        return libdoc

    def _import_resource(self, path):
        ast = ResourceFileBuilder(process_curdir=False).build(
            self._find_resource_file(path))
        return UserLibrary(ast)

    def _find_resource_file(self, path):
        if os.path.isfile(path):
            return os.path.normpath(path)
        for dire in [item for item in sys.path if os.path.isdir(item)]:
            candidate = os.path.normpath(os.path.join(dire, path))
            if os.path.isfile(candidate):
                return candidate
        raise DataError("Resource file '%s' does not exist." % path)

    def _get_doc(self, res):
        if res.doc:
            return unescape(res.doc)
        return "Documentation for resource file ``%s``." % res.name


class KeywordDocBuilder(object):

    def __init__(self, resource=False):
        self._resource = resource

    def build_keywords(self, lib):
        return [self.build_keyword(kw) for kw in lib.handlers]

    def build_keyword(self, kw):
        doc, tags = self._get_doc_and_tags(kw)
        if not self._resource:
            self._escape_strings_in_defaults(kw.arguments.defaults)
        return KeywordDoc(name=kw.name,
                          args=kw.arguments,
                          doc=doc,
                          tags=tags,
                          source=kw.source,
                          lineno=kw.lineno)

    def _escape_strings_in_defaults(self, defaults):
        for name, value in defaults.items():
            if is_string(value):
                value = re.sub(r'[\\\r\n\t]', lambda x: repr(str(x.group()))[1:-1], value)
                value = self._escape_variables(value)
                defaults[name] = re.sub('^(?= )|(?<= )$|(?<= )(?= )', r'\\', value)

    def _escape_variables(self, value):
        result = ''
        match = search_variable(value)
        while match:
            result += r'%s\%s{%s}' % (match.before, match.identifier,
                                      self._escape_variables(match.base))
            for item in match.items:
                result += '[%s]' % self._escape_variables(item)
            match = search_variable(match.after)
        return result + match.string

    def _get_doc_and_tags(self, kw):
        doc = self._get_doc(kw)
        doc, tags = split_tags_from_doc(doc)
        return doc, kw.tags + tags

    def _get_doc(self, kw):
        if self._resource and not isinstance(kw, UserErrorHandler):
            return unescape(kw.doc)
        return kw.doc
