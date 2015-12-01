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

import inspect
import os.path

from robot.errors import DataError
from robot.utils import (Importer, is_string, split_args_from_name_or_path,
                         type_name)

from .listenermethods import (StartSuite, EndSuite, StartTest, EndTest,
                              StartKeyword, EndKeyword, Message, LogMessage,
                              LibraryImport, ResourceImport, VariablesImport,
                              OutputFile, ReportFile, LogFile, XUnitFile,
                              DebugFile, Close)
from .loggerhelper import AbstractLoggerProxy
from .logger import LOGGER


def no_recursion(cls):
    """Class decorator to wrap methods so that they cannot cause recursion.

    Recursion would otherwise happen if one listener logs something and that
    message is received and logged again by log_message or message method.
    """
    def avoid_recursion_wrapper(method):
        def avoid_recursion(self, *args):
            if not self._recursion:
                self._recursion = True
                method(self, *args)
                self._recursion = False
        return avoid_recursion
    for attr, value in cls.__dict__.items():
        if not attr.startswith('_') and inspect.isroutine(value):
            setattr(cls, attr, avoid_recursion_wrapper(value))
    cls._recursion = False
    return cls


@no_recursion
class Listeners(object):

    def __init__(self, listeners):
        listeners = list(self._import_listeners(listeners))
        self._start_suite = StartSuite(listeners)
        self._end_suite = EndSuite(listeners)
        self._start_test = StartTest(listeners)
        self._end_test = EndTest(listeners)
        self._start_keyword = StartKeyword(listeners)
        self._end_keyword = EndKeyword(listeners)
        self._message = Message(listeners)
        self._log_message = LogMessage(listeners)
        self._library_import = LibraryImport(listeners)
        self._resource_import = ResourceImport(listeners)
        self._variables_import = VariablesImport(listeners)
        self._output_file = OutputFile(listeners)
        self._report_file = ReportFile(listeners)
        self._log_file = LogFile(listeners)
        self._xunit_file = XUnitFile(listeners)
        self._debug_file = DebugFile(listeners)
        self._close = Close(listeners)

    def _import_listeners(self, listeners):
        for listener in listeners:
            try:
                yield ListenerProxy(listener)
            except DataError as err:
                if not is_string(listener):
                    listener = type_name(listener)
                LOGGER.error("Taking listener '%s' into use failed: %s"
                             % (listener, err.message))

    def start_suite(self, suite):
        self._start_suite(suite)

    def end_suite(self, suite):
        self._end_suite(suite)

    def start_test(self, test):
        self._start_test(test)

    def end_test(self, test):
        self._end_test(test)

    def start_keyword(self, keyword):
        self._start_keyword(keyword)

    def end_keyword(self, keyword):
        self._end_keyword(keyword)

    def message(self, msg):
        self._message(msg)

    def log_message(self, msg):
        self._log_message(msg)

    def imported(self, import_type, name, attrs):
        method = getattr(self, '_%s_import' % import_type.lower())
        method(name, attrs)

    def output_file(self, file_type, path):
        method = getattr(self, '_%s_file' % file_type.lower())
        method(path)

    def close(self):
        self._close()


class ListenerProxy(AbstractLoggerProxy):
    _methods = ('start_suite', 'end_suite', 'start_test', 'end_test',
                'start_keyword', 'end_keyword', 'log_message', 'message',
                'output_file', 'report_file', 'log_file', 'debug_file',
                'xunit_file', 'close', 'library_import', 'resource_import',
                'variables_import')
    _no_method = None

    def __init__(self, listener):
        listener, name = self._import_listener(listener)
        AbstractLoggerProxy.__init__(self, listener)
        self.name = name
        self.version = self._get_version(listener)

    def _import_listener(self, listener):
        if not is_string(listener):
            return listener, type_name(listener)
        name, args = split_args_from_name_or_path(listener)
        importer = Importer('listener')
        listener = importer.import_class_or_module(os.path.normpath(name),
                                                   instantiate_with_args=args)
        return listener, name

    def _get_version(self, listener):
        try:
            version = int(listener.ROBOT_LISTENER_API_VERSION)
            if version != 2:
                raise ValueError
        except AttributeError:
            raise DataError("Listener '%s' does not have mandatory "
                            "'ROBOT_LISTENER_API_VERSION' attribute."
                            % self.name)
        except (ValueError, TypeError):
            raise DataError("Listener '%s' uses unsupported API version '%s'."
                            % (self.name, listener.ROBOT_LISTENER_API_VERSION))
        return version
