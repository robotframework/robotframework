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

from .listeners import Listeners, ListenerProxy
from .loggerhelper import AbstractLoggerProxy


class LibraryListeners(Listeners):

    def __init__(self):
        self._running_test = False
        self._setup_or_teardown_type = None
        self._global_listeners = {}

    def __nonzero__(self):
        return True

    def _notify_end_test(self, listener, test):
        Listeners._notify_end_test(self, listener, test)
        if listener.library_scope == 'TESTCASE':
            listener.call_method(listener.close)

    def _notify_end_suite(self, listener, suite):
        Listeners._notify_end_suite(self, listener, suite)
        if listener.library_scope == 'TESTSUITE':
            listener.call_method(listener.close)

    def end_suite(self, suite):
        for listener in self._listeners:
            self._notify_end_suite(listener, suite)
        if not suite.parent:
            for listener in self._global_listeners.values():
                listener.call_method(listener.close)

    @property
    def _listeners(self):
        from robot.running import EXECUTION_CONTEXTS
        if not EXECUTION_CONTEXTS.current:
            return []
        listeners = [_LibraryListenerProxy(library) for library in
                     EXECUTION_CONTEXTS.current.namespace.libraries
                     if library.has_listener]
        for listener in listeners:
            if listener.library_scope == 'GLOBAL':
                self._global_listeners[listener.logger] = listener
        return listeners


class _LibraryListenerProxy(ListenerProxy):

    def __init__(self, library):
        AbstractLoggerProxy.__init__(self, library.listener)
        self.name = type(library).__name__
        self.version = self._get_version(library.listener)
        self.is_java = self._is_java(library.listener)
        self.library_scope = library.scope

    def _get_method_names(self, name):
        names = ListenerProxy._get_method_names(self, name)
        return names + ['_' + name for name in names]

