#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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


import os.path
import copy

from robot.parsing import ResourceFile
from robot.output import LOGGER
from robot import utils

from testlibraries import TestLibrary
from userkeyword import UserLibrary


class Importer:

    def __init__(self):
        self._libraries = _LibraryCache()
        self._resources = _LibraryCache()

    def import_library(self, name, args):
        code_name, name, args = self._get_lib_names_and_args(name, args)
        lib = self._import_library(code_name, args)
        if code_name != name:
            lib = self._copy_library(lib, name)
            LOGGER.info("Imported library '%s' with name '%s'" % (code_name, name))
        return lib

    def import_resource(self, path):
        if self._resources.has_key(path):
            LOGGER.info("Found resource file '%s' from cache" % path)
        else:
            resource = ResourceFile(path)
            resource.user_keywords = UserLibrary(resource.user_keywords, path)
            self._resources[path] = resource
            LOGGER.info("Imported resource file '%s' (%d keywords)"
                        % (path, len(resource.user_keywords)))
            # Resource file may contain only variables so we should not warn
            # if there are no keywords. Importing an empty resource file fails
            # already earlier so no need to check that here either.
        return self._resources[path]

    def _get_lib_names_and_args(self, name, args):
        # Ignore spaces unless importing by path
        if not os.path.exists(name):
            name = name.replace(' ', '')
        args = utils.to_list(args)
        if len(args) >= 2 and utils.is_str(args[-2]) \
               and args[-2].upper() == 'WITH NAME':
            lib_name = args[-1].replace(' ', '')
            args = args[:-2]
        else:
            lib_name = name
        return name, lib_name, args

    def _import_library(self, name, args):
        key = (name, args)
        if self._libraries.has_key(key):
            LOGGER.info("Found test library '%s' with arguments %s from cache"
                        % (name, utils.seq2str2(args)))
            return self._libraries[key]
        lib = TestLibrary(name, args)
        self._libraries[key] = lib
        libtype = lib.__class__.__name__.replace('Library', '').lower()[1:]
        LOGGER.info("Imported library '%s' with arguments %s (version %s, "
                    "%s type, %s scope, %d keywords, source %s)"
                    % (name, utils.seq2str2(args), lib.version, libtype,
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

