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

from robot.output import LOGGER
from robot.errors import FrameworkError, DataError
from robot.utils import normpath, seq2str, seq2str2

from .builder import ResourceFileBuilder
from .testlibraries import TestLibrary


RESOURCE_EXTENSIONS = {'.resource', '.robot', '.txt', '.tsv', '.rst', '.rest',
                       '.json', '.rsrc'}


class Importer:

    def __init__(self):
        self._library_cache = ImportCache()
        self._resource_cache = ImportCache()

    def reset(self):
        self.__init__()

    def close_global_library_listeners(self):
        for lib in self._library_cache.values():
            lib.scope_manager.close_global_listeners()

    def import_library(self, name, args, alias, variables):
        lib = TestLibrary.from_name(name, args=args, variables=variables,
                                    create_keywords=False)
        positional, named = lib.init.positional, lib.init.named
        args_str = seq2str2(positional + [f'{n}={named[n]}' for n in named])
        key = (name, positional, named)
        if key in self._library_cache:
            LOGGER.info(f"Found library '{name}' with arguments {args_str} "
                        f"from cache.")
            lib = self._library_cache[key]
        else:
            lib.create_keywords()
            if lib.scope is not lib.scope.GLOBAL:
                lib.instance = None
            self._library_cache[key] = lib
            self._log_imported_library(name, args_str, lib)
        if alias:
            alias = variables.replace_scalar(alias)
            lib = lib.copy(name=alias)
            LOGGER.info(f"Imported library '{name}' with name '{alias}'.")
        return lib

    def import_resource(self, path, lang=None):
        self._validate_resource_extension(path)
        if path in self._resource_cache:
            LOGGER.info(f"Found resource file '{path}' from cache.")
        else:
            resource = ResourceFileBuilder(lang=lang).build(path)
            self._resource_cache[path] = resource
        return self._resource_cache[path]

    def _validate_resource_extension(self, path):
        extension = os.path.splitext(path)[1]
        if extension.lower() not in RESOURCE_EXTENSIONS:
            extensions = seq2str(sorted(RESOURCE_EXTENSIONS))
            raise DataError(f"Invalid resource file extension '{extension}'. "
                            f"Supported extensions are {extensions}.")

    def _log_imported_library(self, name, args_str, lib):
        kind = type(lib).__name__.replace('Library', '').lower()
        listener = ', with listener' if lib.listeners else ''
        LOGGER.info(f"Imported library '{name}' with arguments {args_str} "
                    f"(version {lib.version or '<unknown>'}, {kind} type, "
                    f"{lib.scope.name} scope, {len(lib.keywords)} keywords{listener}).")
        if not (lib.keywords or lib.listeners):
            LOGGER.warn(f"Imported library '{name}' contains no keywords.")


class ImportCache:
    """Keeps track on and optionally caches imported items.

    Handles paths in keys case-insensitively on case-insensitive OSes.
    Unlike dicts, this storage accepts mutable values in keys.
    """

    def __init__(self):
        self._keys = []
        self._items = []

    def __setitem__(self, key, item):
        if not isinstance(key, (str, tuple)):
            raise FrameworkError('Invalid key for ImportCache')
        key = self._norm_path_key(key)
        if key not in self._keys:
            self._keys.append(key)
            self._items.append(item)
        else:
            self._items[self._keys.index(key)] = item

    def add(self, key, item=None):
        self.__setitem__(key, item)

    def __getitem__(self, key):
        key = self._norm_path_key(key)
        if key not in self._keys:
            raise KeyError
        return self._items[self._keys.index(key)]

    def __contains__(self, key):
        return self._norm_path_key(key) in self._keys

    def values(self):
        return self._items

    def _norm_path_key(self, key):
        if self._is_path(key):
            return normpath(key, case_normalize=True)
        if isinstance(key, tuple):
            return tuple(self._norm_path_key(k) for k in key)
        return key

    def _is_path(self, key):
        return isinstance(key, str) and os.path.isabs(key) and os.path.exists(key)
