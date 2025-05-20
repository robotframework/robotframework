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

from typing import Any

from .normalizing import NormalizedDict

Connection = Any


class ConnectionCache:
    """Cache for libraries to use with concurrent connections, processes, etc.

    The cache stores the registered connections (or other objects) and allows
    switching between them using generated indices, user given aliases or
    connection objects themselves. This is useful with any library having a need
    for multiple concurrent connections, processes, etc.

    This class is used also outside the core framework by SeleniumLibrary,
    SSHLibrary, etc. Backwards compatibility is thus important when doing changes.
    """

    def __init__(self, no_current_msg="No open connection."):
        self._no_current = NoConnection(no_current_msg)
        self.current = self._no_current  #: Current active connection.
        self._connections = []
        self._aliases = NormalizedDict[int]()

    @property
    def current_index(self) -> "int|None":
        if not self:
            return None
        for index, conn in enumerate(self):
            if conn is self.current:
                return index + 1

    @current_index.setter
    def current_index(self, index: "int|None"):
        if index is None:
            self.current = self._no_current
        else:
            self.current = self._connections[index - 1]

    def register(self, connection: Connection, alias: "str|None" = None):
        """Registers given connection with optional alias and returns its index.

        Given connection is set to be the :attr:`current` connection.

        If alias is given, it must be a string. Aliases are case and space
        insensitive.

        The index of the first connection after initialization, and after
        :meth:`close_all` or :meth:`empty_cache`, is 1, second is 2, etc.
        """
        self.current = connection
        self._connections.append(connection)
        index = len(self._connections)
        if alias:
            self._aliases[alias] = index
        return index

    def switch(self, identifier: "int|str|Connection") -> Connection:
        """Switches to the connection specified using the ``identifier``.

        Identifier can be an index, an alias, or a registered connection.
        Raises an error if no matching connection is found.

        Updates :attr:`current` and also returns its new value.
        """
        self.current = self.get_connection(identifier)
        return self.current

    def get_connection(
        self,
        identifier: "int|str|Connection|None" = None,
    ) -> Connection:
        """Returns the connection specified using the ``identifier``.

        Identifier can be an index (integer or string), an alias, a registered
        connection or ``None``. If the identifier is ``None``, returns the
        current connection if it is active and raises an error if it is not.
        Raises an error also if no matching connection is found.
        """
        if identifier is None:
            if not self:
                self.current.raise_error()
            return self.current
        try:
            index = self.get_connection_index(identifier)
        except ValueError as err:
            raise RuntimeError(err.args[0])
        return self._connections[index - 1]

    def get_connection_index(self, identifier: "int|str|Connection") -> int:
        """Returns the index of the connection specified using the ``identifier``.

        Identifier can be an index (integer or string), an alias, or a registered
        connection.

        New in Robot Framework 7.0. :meth:`resolve_alias_or_index` can be used
        with earlier versions.
        """
        if isinstance(identifier, str) and identifier in self._aliases:
            return self._aliases[identifier]
        if identifier in self._connections:
            return self._connections.index(identifier) + 1
        try:
            index = int(identifier)
        except (ValueError, TypeError):
            index = -1
        if 0 < index <= len(self._connections):
            return index
        raise ValueError(f"Non-existing index or alias '{identifier}'.")

    def resolve_alias_or_index(self, alias_or_index):
        """Deprecated in RF 7.0. Use :meth:`get_connection_index` instead."""
        # This was initially added for SeleniumLibrary in RF 3.1.2.
        # https://github.com/robotframework/robotframework/issues/3125
        # The new method was added in RF 7.0. We can loudly deprecate this
        # earliest in RF 8.0.
        return self.get_connection_index(alias_or_index)

    def close_all(self, closer_method: str = "close"):
        """Closes connections using the specified closer method and empties cache.

        If simply calling the closer method is not adequate for closing
        connections, clients should close connections themselves and use
        :meth:`empty_cache` afterward.
        """
        for conn in self._connections:
            getattr(conn, closer_method)()
        self.empty_cache()
        return self.current

    def empty_cache(self):
        """Empties the connection cache.

        Indexes of the new connections starts from 1 after this.
        """
        self.current = self._no_current
        self._connections = []
        self._aliases = NormalizedDict()

    __getitem__ = get_connection

    def __iter__(self):
        return iter(self._connections)

    def __len__(self):
        return len(self._connections)

    def __bool__(self):
        return self.current is not self._no_current


class NoConnection:

    def __init__(self, message):
        self.message = message

    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError
        self.raise_error()

    def raise_error(self):
        raise RuntimeError(self.message)

    def __bool__(self):
        return False
