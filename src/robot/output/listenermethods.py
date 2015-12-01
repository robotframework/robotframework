#  Copyright 2008-2015 Nokia Solutions and Networks
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

from contextlib import contextmanager

from robot.utils import get_error_details, py2to3

from .listenerarguments import (StartSuiteArguments, EndSuiteArguments,
                                StartTestArguments, EndTestArguments,
                                StartKeywordArguments, EndKeywordArguments,
                                MessageArguments, ListenerArguments)
from .logger import LOGGER


@py2to3
class ListenerMethod(object):
    _method_name = None
    _argument_handler = ListenerArguments

    def __init__(self, listeners):
        self._methods = self._get_methods(listeners)
        self._get_arguments = self._argument_handler().get_arguments

    def _get_methods(self, listeners):
        methods = []
        for listener in listeners:
            method = getattr(listener, self._method_name)
            if method:
                methods.append((method, listener))
        return methods

    def __nonzero__(self):
        return bool(self._methods)

    def __call__(self, *args):
        if self._methods:
            args = self._get_arguments(*args)
            for method, listener in self._methods:
                with self._error_handler(method, listener):
                    method(*args)

    @contextmanager
    def _error_handler(self, method, listener):
        try:
            yield
        except:
            message, details = get_error_details()
            LOGGER.error("Calling method '%s' of listener '%s' failed: %s"
                         % (method.__name__, listener.name, message))
            LOGGER.info("Details:\n%s" % details)


class StartSuite(ListenerMethod):
    _method_name = 'start_suite'
    _argument_handler = StartSuiteArguments


class EndSuite(ListenerMethod):
    _method_name = 'end_suite'
    _argument_handler = EndSuiteArguments


class StartTest(ListenerMethod):
    _method_name = 'start_test'
    _argument_handler = StartTestArguments


class EndTest(ListenerMethod):
    _method_name = 'end_test'
    _argument_handler = EndTestArguments


class StartKeyword(ListenerMethod):
    _method_name = 'start_keyword'
    _argument_handler = StartKeywordArguments


class EndKeyword(ListenerMethod):
    _method_name = 'end_keyword'
    _argument_handler = EndKeywordArguments


class Message(ListenerMethod):
    _method_name = 'message'
    _argument_handler = MessageArguments


class LogMessage(ListenerMethod):
    _method_name = 'log_message'
    _argument_handler = MessageArguments


class LibraryImport(ListenerMethod):
    _method_name = 'library_import'


class ResourceImport(ListenerMethod):
    _method_name = 'resource_import'


class VariablesImport(ListenerMethod):
    _method_name = 'variables_import'


class OutputFile(ListenerMethod):
    _method_name = 'output_file'


class ReportFile(ListenerMethod):
    _method_name = 'report_file'


class LogFile(ListenerMethod):
    _method_name = 'log_file'


class XUnitFile(ListenerMethod):
    _method_name = 'xunit_file'


class DebugFile(ListenerMethod):
    _method_name = 'debug_file'


class Close(ListenerMethod):
    _method_name = 'close'
