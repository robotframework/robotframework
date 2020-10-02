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
import re
import sys
try:
    from enum import Enum
except ImportError:    # Standard in Py 3.4+ but can be separately installed
    class Enum(object):
        pass

from robot.errors import DataError
from robot.running import (TestLibrary, UserLibrary, UserErrorHandler,
                           ResourceFileBuilder)
from robot.utils import split_tags_from_doc, unescape, unic

from .model import LibraryDoc, KeywordDoc, ArgumentDoc, DefaultValue


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
        return KeywordDoc(name=kw.name,
                          args=self._get_args(kw.arguments),
                          doc=doc,
                          tags=tags,
                          source=kw.source,
                          lineno=kw.lineno)

    def _get_doc_and_tags(self, kw):
        doc = self._get_doc(kw)
        doc, tags = split_tags_from_doc(doc)
        return doc, kw.tags + tags

    def _get_doc(self, kw):
        if self._resource and not isinstance(kw, UserErrorHandler):
            return unescape(kw.doc)
        return kw.doc

    def _get_args(self, argspec):
        """:type argspec: :py:class:`robot.running.arguments.ArgumentSpec`"""
        arguments = []
        for arg_name in argspec.positional:
            arguments.append(
                self._get_scalar_arg_doc(argspec, arg_name, 'POSITIONAL_OR_KEYWORD'))
        if argspec.varargs:
            value_type = self._get_value_type(argspec, argspec.varargs)
            arguments.append(ArgumentDoc(name=argspec.varargs,
                                         type=value_type,
                                         kind='VAR_POSITIONAL',
                                         required=False))
        for arg_name in argspec.kwonlyargs:
            arguments.append(
                self._get_scalar_arg_doc(argspec, arg_name, 'KEYWORD_ONLY'))

        if argspec.kwargs:
            value_type = self._get_value_type(argspec, argspec.kwargs)
            arguments.append(ArgumentDoc(name=argspec.kwargs,
                                         type=value_type,
                                         kind='VAR_KEYWORD',
                                         required=False))
        return arguments

    def _get_scalar_arg_doc(self, argspec, arg_name, arg_type):
        if arg_name in argspec.defaults:
            robot_default = self._escape_defaults_str(argspec.defaults[arg_name])
            default = DefaultValue(robot_default)
        else:
            default = None
        value_type = self._get_value_type(argspec, arg_name)
        return ArgumentDoc(name=arg_name,
                           type=value_type,
                           default=default,
                           kind=arg_type,
                           required=arg_name not in argspec.defaults)

    @staticmethod
    def _get_value_type(argspec, argument):
        if argspec.types and argument in argspec.types:
            return argspec.types[argument]

    @staticmethod
    def _escape_defaults_str(value):
        if isinstance(value, Enum):
            return value.name
        if isinstance(value, str):
            if value == '':
                return '${Empty}'
            value_repr = repr(value)[1:-1]
            return re.sub('^(?= )|(?<= )$|(?<= )(?= )', r'\\', value_repr)
        return unic(value)