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

from . import pyloggingconf
from .debugfile import DebugFile
from .listeners import LibraryListeners, Listeners
from .logger import LOGGER, LoggerProxy
from .loggerapi import LoggerApi
from .loggerhelper import AbstractLogger
from .xmllogger import XmlLogger, FlatXmlLogger


class Output(AbstractLogger, LoggerApi):

    def __init__(self, settings):
        AbstractLogger.__init__(self)
        self._xmllogger = XmlLogger(settings.output, settings.log_level,
                                    settings.rpa)
        self._flat_xml_logger = None
        self.listeners = Listeners(settings.listeners, settings.log_level)
        self.library_listeners = LibraryListeners(settings.log_level)
        self._register_loggers(DebugFile(settings.debug_file))
        self._settings = settings
        self._flatten_level = 0

    @property
    def flat_xml_logger(self):
        if self._flat_xml_logger is None:
            self._flat_xml_logger = FlatXmlLogger(self._xmllogger)
        return self._flat_xml_logger

    def _register_loggers(self, debug_file):
        LOGGER.register_xml_logger(self._xmllogger)
        LOGGER.register_listeners(self.listeners or None, self.library_listeners)
        if debug_file:
            LOGGER.register_logger(debug_file)

    def register_error_listener(self, listener):
        LOGGER.register_error_listener(listener)

    def close(self, result):
        self._xmllogger.visit_statistics(result.statistics)
        self._xmllogger.close()
        LOGGER.unregister_xml_logger()
        LOGGER.output_file('Output', self._settings['Output'])

    def start_suite(self, data, result):
        LOGGER.start_suite(data, result)

    def end_suite(self, data, result):
        LOGGER.end_suite(data, result)

    def start_test(self, data, result):
        LOGGER.start_test(data, result)

    def end_test(self, data, result):
        LOGGER.end_test(data, result)

    def start_keyword(self, data, result):
        LOGGER.start_keyword(data, result)
        if result.type in result.KEYWORD_TYPES and result.tags.robot('flatten'):
            self._flatten_level += 1
            if self._flatten_level == 1:
                LOGGER._xml_logger = LoggerProxy(self.flat_xml_logger)

    def end_keyword(self, data, result):
        if result.type in result.KEYWORD_TYPES and result.tags.robot('flatten'):
            self._flatten_level -= 1
            if not self._flatten_level:
                LOGGER._xml_logger = LoggerProxy(self._xmllogger)
        LOGGER.end_keyword(data, result)

    def start_for(self, data, result):
        LOGGER.start_for(data, result)

    def end_for(self, data, result):
        LOGGER.end_for(data, result)

    def start_for_iteration(self, data, result):
        LOGGER.start_keyword(data, result)

    def end_for_iteration(self, data, result):
        LOGGER.end_keyword(data, result)

    def start_while(self, data, result):
        LOGGER.start_keyword(data, result)

    def end_while(self, data, result):
        LOGGER.end_keyword(data, result)

    def start_while_iteration(self, data, result):
        LOGGER.start_keyword(data, result)

    def end_while_iteration(self, data, result):
        LOGGER.end_keyword(data, result)

    def start_if(self, data, result):
        LOGGER.start_keyword(data, result)

    def end_if(self, data, result):
        LOGGER.end_keyword(data, result)

    def start_if_branch(self, data, result):
        LOGGER.start_keyword(data, result)

    def end_if_branch(self, data, result):
        LOGGER.end_keyword(data, result)

    def start_try(self, data, result):
        LOGGER.start_keyword(data, result)

    def end_try(self, data, result):
        LOGGER.end_keyword(data, result)

    def start_try_branch(self, data, result):
        LOGGER.start_keyword(data, result)

    def end_try_branch(self, data, result):
        LOGGER.end_keyword(data, result)

    def start_break(self, data, result):
        LOGGER.start_keyword(data, result)

    def end_break(self, data, result):
        LOGGER.end_keyword(data, result)

    def start_continue(self, data, result):
        LOGGER.start_keyword(data, result)

    def end_continue(self, data, result):
        LOGGER.end_keyword(data, result)

    def start_return(self, data, result):
        LOGGER.start_keyword(data, result)

    def end_return(self, data, result):
        LOGGER.end_keyword(data, result)

    def start_error(self, data, result):
        LOGGER.start_keyword(data, result)

    def end_error(self, data, result):
        LOGGER.end_keyword(data, result)

    def message(self, msg):
        LOGGER.log_message(msg)

    def trace(self, msg, write_if_flat=True):
        if write_if_flat or self._flatten_level == 0:
            self.write(msg, 'TRACE')

    def set_log_level(self, level):
        pyloggingconf.set_level(level)
        self.listeners.set_log_level(level)
        self.library_listeners.set_log_level(level)
        return self._xmllogger.set_log_level(level)
