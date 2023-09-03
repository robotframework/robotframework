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
from robot.running import (ArgInfo, ResourceFileBuilder, TestLibrary, TestSuiteBuilder,
                           TypeInfo, UserLibrary, UserErrorHandler)
from robot.utils import is_string, split_tags_from_doc, unescape
from robot.variables import search_variable

from .datatypes import TypeDoc
from .model import LibraryDoc, KeywordDoc


class LibraryDocBuilder:
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
        libdoc.type_docs = self._get_type_docs(libdoc.inits + libdoc.keywords,
                                               lib.converters)
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
        return lib.doc or f"Documentation for library ``{lib.name}``."

    def _get_initializers(self, lib):
        if lib.init.arguments:
            return [KeywordDocBuilder().build_keyword(lib.init)]
        return []

    def _get_type_docs(self, keywords, custom_converters):
        type_docs = {}
        for kw in keywords:
            for arg in kw.args:
                kw.type_docs[arg.name] = {}
                for type_info in self._yield_type_info(arg.type):
                    type_doc = TypeDoc.for_type(type_info.type, custom_converters)
                    if type_doc:
                        kw.type_docs[arg.name][type_info.name] = type_doc.name
                        type_docs.setdefault(type_doc, set()).add(kw.name)
        for type_doc, usages in type_docs.items():
            type_doc.usages = sorted(usages, key=str.lower)
        return set(type_docs)

    def _yield_type_info(self, info: TypeInfo):
        if not info.is_union:
            yield info
        for nested in info.nested:
            yield from self._yield_type_info(nested)


class ResourceDocBuilder:
    type = 'RESOURCE'

    def build(self, path):
        path = self._find_resource_file(path)
        res, name = self._import_resource(path)
        libdoc = LibraryDoc(name=name,
                            doc=self._get_doc(res, name),
                            type=self.type,
                            scope='GLOBAL',
                            source=res.source,
                            lineno=1)
        libdoc.keywords = KeywordDocBuilder(resource=True).build_keywords(res)
        return libdoc

    def _import_resource(self, path):
        model = ResourceFileBuilder(process_curdir=False).build(path)
        resource = UserLibrary(model)
        return resource, resource.name

    def _find_resource_file(self, path):
        if os.path.isfile(path):
            return os.path.normpath(os.path.abspath(path))
        for dire in [item for item in sys.path if os.path.isdir(item)]:
            candidate = os.path.normpath(os.path.join(dire, path))
            if os.path.isfile(candidate):
                return os.path.abspath(candidate)
        raise DataError(f"Resource file '{path}' does not exist.")

    def _get_doc(self, resource, name):
        if resource.doc:
            return unescape(resource.doc)
        return f"Documentation for resource file ``{name}``."


class SuiteDocBuilder(ResourceDocBuilder):
    type = 'SUITE'

    def _import_resource(self, path):
        builder = TestSuiteBuilder(process_curdir=False)
        if os.path.basename(path).lower() == '__init__.robot':
            path = os.path.dirname(path)
            builder.included_suites = ()
            builder.allow_empty_suite = True
        suite = builder.build(path)
        return UserLibrary(suite.resource), suite.name

    def _get_doc(self, resource, name):
        return f"Documentation for keywords in suite ``{name}``."


class KeywordDocBuilder:

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
                          private=tags.robot('private'),
                          deprecated=doc.startswith('*DEPRECATED') and '*' in doc[1:],
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
