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

import os
import sys

from robot.errors import DataError
from robot.running import TestLibrary, UserLibrary
from robot.parsing import populators
from robot import utils

from .librarydoc import LibraryDoc, KeywordDoc


class LibraryDocBuilder(object):

    def build(self, library, arguments=None):
        lib = TestLibrary(library, arguments)
        libdoc = LibraryDoc(name=lib.name,
                            doc=self._get_doc(lib),
                            version=lib.version,
                            scope=self._get_scope(lib),
                            named_args=lib.supports_named_arguments)
        libdoc.inits = self._get_initializers(lib)
        libdoc.keywords = KeywordDocBuilder().build_keywords(lib)
        return libdoc

    def _get_doc(self, lib):
        return lib.doc or "Documentation for test library `%s`." % lib.name

    def _get_scope(self, lib):
        if hasattr(lib, 'scope'):
            return {'TESTCASE': 'test case', 'TESTSUITE': 'test suite',
                    'GLOBAL': 'global'}[lib.scope]
        return ''

    def _get_initializers(self, lib):
        if lib.init.arguments.maxargs:
            return [KeywordDocBuilder().build_keyword(lib.init)]
        return []


class ResourceDocBuilder(object):

    def build(self, path):
        res = self._import_resource(path)
        libdoc = LibraryDoc(name=res.name,
                            doc=self._get_doc(res),
                            type='resource',
                            named_args=True)
        libdoc.keywords = KeywordDocBuilder().build_keywords(res)
        return libdoc

    def _import_resource(self, path):
        populators.PROCESS_CURDIR = False
        try:
            return UserLibrary(self._find_resource_file(path))
        finally:
            populators.PROCESS_CURDIR = True

    def _find_resource_file(self, path):
        if os.path.isfile(path):
            return path
        for dire in [item for item in sys.path if os.path.isdir(item)]:
            if os.path.isfile(os.path.join(dire, path)):
                return os.path.join(dire, path)
        raise DataError("Resource file '%s' does not exist." % path)

    def _get_doc(self, res):
        doc = res.doc or "Documentation for resource file `%s`." % res.name
        return utils.unescape(doc)


class KeywordDocBuilder(object):

    def build_keywords(self, lib):
        return [self.build_keyword(kw) for kw in lib.handlers.values()]

    def build_keyword(self, kw):
        return KeywordDoc(name=kw.name, args=self._get_args(kw), doc=kw.doc)

    def _get_args(self, kw):
        required, defaults = self._parse_args(kw)
        args = required + ['%s=%s' % item for item in defaults]
        varargs = self._normalize_arg(kw.arguments.varargs, kw.type)
        if varargs:
            args.append('*%s' % varargs)
        return args

    def _parse_args(self, kw):
        args = [self._normalize_arg(arg, kw.type) for arg in kw.arguments.names]
        default_count = len(kw.arguments.defaults)
        if not default_count:
            return args, []
        required = args[:-default_count]
        defaults = zip(args[-default_count:], kw.arguments.defaults)
        return required, defaults

    def _normalize_arg(self, arg, kw_type):
        if arg and kw_type == 'user':
            arg = arg[2:-1]  # strip ${} to make args look consistent
        return arg
