#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

import copy

from robot.output import LOGGER
from robot.parsing import ResourceFile
from robot import utils

from testlibraries import TestLibrary


class Importer:

    def __init__(self):
        self._libraries = _LibraryCache()
        self._resources = _LibraryCache()

    def import_library(self, name, args, alias, variables):
        lib = TestLibrary(name, args, variables, create_handlers=False)
        positional, named = lib.positional_args, lib.named_args
        lib = self._import_library(name, positional, named, lib)
        if alias and name != alias:
            lib = self._copy_library(lib, alias)
            LOGGER.info("Imported library '%s' with name '%s'" % (name, alias))
        return lib

    def import_resource(self, path):
        if self._resources.has_key(path):
            LOGGER.info("Found resource file '%s' from cache" % path)
        else:
            resource = ResourceFile(path)
            self._resources[path] = resource
        return self._resources[path]

    def _import_library(self, name, positional, named, lib):
        key = (name, positional, named)
        if self._libraries.has_key(key):
            LOGGER.info("Found test library '%s' with arguments %s from cache"
                        % (name, utils.seq2str2(positional)))
            return self._libraries[key]
        lib.create_handlers()
        self._libraries[key] = lib
        libtype = lib.__class__.__name__.replace('Library', '').lower()[1:]
        LOGGER.info("Imported library '%s' with arguments %s (version %s, "
                    "%s type, %s scope, %d keywords, source %s)"
                    % (name, utils.seq2str2(positional), lib.version, libtype,
                       lib.scope.lower(), len(lib), lib.source))
        if len(lib) == 0:
            LOGGER.warn("Imported library '%s' contains no keywords" % name)
        return lib

    def _copy_library(self, lib, newname):
        libcopy = copy.copy(lib)
        libcopy.name = newname
        libcopy.init_scope_handling()
        libcopy.handlers = utils.NormalizedDict(ignore=['_'])
        for handler in lib.handlers.values():
            handcopy = copy.copy(handler)
            handcopy.library = libcopy
            libcopy.handlers[handler.name] = handcopy
        return libcopy


class _LibraryCache:
    """Cache for libs/resources that doesn't require mutable keys like dicts"""

    def __init__(self):
        self._keys = []
        self._libs = []

    def __setitem__(self, key, library):
        self._keys.append(key)
        self._libs.append(library)

    def __getitem__(self, key):
        try:
            return self._libs[self._keys.index(key)]
        except ValueError:
            raise KeyError

    def has_key(self, key):
        return key in self._keys

