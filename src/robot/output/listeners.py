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

import os.path
from collections.abc import Sequence

from robot.errors import DataError
from robot.utils import Importer, split_args_from_name_or_path, type_name

from .listenerfacade import ListenerFacade
from .logger import LOGGER
from .loglevel import LogLevel, SettableLevel


class Listeners:
    _listeners: list

    def __init__(
        self,
        listeners: "Sequence[str | object]" = (),
        log_level: "LogLevel | SettableLevel" = "INFO",
    ):
        if isinstance(log_level, str):
            log_level = LogLevel(log_level)
        self._log_level = log_level
        self._listeners = self._import_listeners(listeners)

    @property
    def listeners(self):
        return self._listeners

    def _import_listeners(self, listeners, library=None) -> "list[ListenerFacade]":
        imported = []
        for listener in listeners:
            if library and isinstance(listener, str) and listener.upper() == "SELF":
                listener = library.instance
            try:
                facade = create_listener_facade(listener, self._log_level, library)
            except DataError as err:
                if library:
                    raise
                LOGGER.error(str(err))
            else:
                imported.append(facade)
        return imported

    def __iter__(self):
        return iter(self.listeners)

    def __len__(self):
        return len(self.listeners)


class LibraryListeners(Listeners):

    def __init__(self, log_level: "LogLevel | str" = "INFO"):
        super().__init__(log_level=log_level)

    @property
    def listeners(self):
        return self._listeners[-1] if self._listeners else []

    def new_suite_scope(self):
        self._listeners.append([])

    def discard_suite_scope(self):
        self._listeners.pop()

    def register(self, library):
        listeners = self._import_listeners(library.listeners, library=library)
        self._listeners[-1].extend(listeners)

    def unregister(self, library, close=False):
        remaining = []
        for listener in self._listeners[-1]:
            if listener.library is not library:
                remaining.append(listener)
            elif close:
                listener.close()
        self._listeners[-1] = remaining


def create_listener_facade(
    listener: "str | object",
    log_level: "LogLevel | SettableLevel" = "INFO",
    library: object = None,
) -> ListenerFacade:
    if isinstance(log_level, str):
        log_level = LogLevel(log_level)
    try:
        listener_obj, name = _import_listener(listener)
        return ListenerFacade.from_object(
            listener_obj,
            log_level,
            library,
            error=LOGGER.error,
            info=LOGGER.info,
            name=name,
        )
    except DataError as err:
        name = listener if isinstance(listener, str) else type_name(listener)
        raise DataError(f"Taking listener '{name}' into use failed: {err}")


def _import_listener(listener: "str | object") -> "tuple[object, str | None]":
    if isinstance(listener, str):
        name, args = split_args_from_name_or_path(listener)
        name = os.path.normpath(name)
        importer = Importer("listener", logger=LOGGER)
        try:
            return importer.import_class_or_module(
                name,
                instantiate_with_args=args,
            ), name
        except DataError as err:
            raise err
    return listener, None
