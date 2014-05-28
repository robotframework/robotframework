#  Copyright 2008-2014 Nokia Solutions and Networks
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

from .listeners import Listeners, _ListenerProxy
from .loggerhelper import AbstractLoggerProxy


class LibraryListeners(Listeners):

    def __init__(self):
        self._running_test = False
        self._setup_or_teardown_type = None

    def __nonzero__(self):
        return True

    @property
    def _listeners(self):
        from robot.running import EXECUTION_CONTEXTS
        if not EXECUTION_CONTEXTS.current:
            return []
        return [_LibraryListenerProxy(listener) for listener in
                EXECUTION_CONTEXTS.current.namespace.library_listeners]

class _LibraryListenerProxy(_ListenerProxy):

    def __init__(self, listener):
        AbstractLoggerProxy.__init__(self, listener)
        self.name = type(listener).__name__
        self.version = self._get_version(listener)
        self.is_java = self._is_java(listener)

    def _get_method_names(self, name):
        return (name, self._toCamelCase(name), '_%s' % name, '_%s' % self._toCamelCase(name))
