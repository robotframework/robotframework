#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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

from .normalizing import NormalizedDict


class ConnectionCache(object):
    """Cache for test libs to use with concurrent connections, processes, etc.

    The cache stores the registered connections (or other objects) and allows
    switching between them using generated indices or user given aliases.
    This is useful with any test library where there's need for multiple
    concurrent connections, processes, etc.

    This class can, and is, used also outside the core framework by SSHLibrary,
    Selenium(2)Library, etc. Backwards compatibility is thus important when
    doing changes.
    """

    def __init__(self, no_current_msg='No open connection.'):
        self.current = self._no_current = NoConnection(no_current_msg)
        self._connections = []
        self._aliases = NormalizedDict()

    def _get_current_index(self):
        return self._connections.index(self.current) + 1 if self else None

    def _set_current_index(self, index):
        self.current = self._connections[index - 1] \
            if index is not None else self._no_current

    current_index = property(_get_current_index, _set_current_index)

    def register(self, connection, alias=None):
        """Registers given connection with optional alias and returns its index.

        Given connection is set to be the current connection. Alias must be
        a string. The index of the first connection after initialization or
        close_all or empty_cache is 1, second is 2, etc.
        """
        self.current = connection
        self._connections.append(connection)
        if isinstance(alias, basestring):
            self._aliases[alias] = self.current_index
        return self.current_index

    def switch(self, index_or_alias):
        """Switches to the connection specified by given index or alias.

        If alias is given it must be a string. Indexes can be either integers
        or strings that can be converted into integer. Raises RuntimeError
        if no connection with given index or alias found.
        """
        self.current = self.get_connection(index_or_alias)
        return self.current

    def get_connection(self, index_or_alias):
        """Get the connection specified by given index or alias.

        If alias is given it must be a string. Indexes can be either integers
        or strings that can be converted into integer. Raises RuntimeError
        if no connection with given index or alias found.
        """
        try:
            index = self._resolve_index_or_alias(index_or_alias)
        except ValueError:
            raise RuntimeError("Non-existing index or alias '%s'."
                               % index_or_alias)
        return self._connections[index-1]

    def close_all(self, closer_method='close'):
        """Closes connections using given closer method and empties cache.

        If simply calling the closer method is not adequate for closing
        connections, clients should close connections themselves and use
        empty_cache afterwards.
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

    def __iter__(self):
        return iter(self._connections)

    def __len__(self):
        return len(self._connections)

    def __nonzero__(self):
        return self.current is not self._no_current

    def _resolve_index_or_alias(self, index_or_alias):
        try:
            return self._resolve_alias(index_or_alias)
        except ValueError:
            return self._resolve_index(index_or_alias)

    def _resolve_alias(self, alias):
        if isinstance(alias, basestring):
            try:
                return self._aliases[alias]
            except KeyError:
                pass
        raise ValueError

    def _resolve_index(self, index):
        index = int(index)
        if not 0 < index <= len(self._connections):
            raise ValueError
        return index


class NoConnection(object):

    def __init__(self, msg):
        self._msg = msg

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError
        raise RuntimeError(self._msg)

    def __nonzero__(self):
        return False
