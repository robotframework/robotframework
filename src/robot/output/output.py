#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

from robot.common.statistics import Statistics

from .listeners import Listeners
from .logger import LOGGER
from .loggerhelper import AbstractLogger
from .debugfile import DebugFile
from .xmllogger import XmlLogger


class Output(AbstractLogger):

    def __init__(self, settings):
        AbstractLogger.__init__(self)
        self._xmllogger = XmlLogger(settings['Output'], settings['LogLevel'])
        self._register_loggers(settings['Listeners'], settings['DebugFile'])
        self._settings = settings

    def _register_loggers(self, listeners, debugfile):
        LOGGER.register_context_changing_logger(self._xmllogger)
        for logger in Listeners(listeners), DebugFile(debugfile):
            if logger: LOGGER.register_logger(logger)
        LOGGER.disable_message_cache()

    def close(self, suite):
        stats = Statistics(suite, self._settings['SuiteStatLevel'],
                           self._settings['TagStatInclude'],
                           self._settings['TagStatExclude'],
                           self._settings['TagStatCombine'],
                           self._settings['TagDoc'],
                           self._settings['TagStatLink'])
        stats.serialize(self._xmllogger)
        self._xmllogger.close()
        LOGGER.unregister_logger(self._xmllogger)
        LOGGER.output_file('Output', self._settings['Output'])

    def start_suite(self, suite):
        LOGGER.start_suite(suite)

    def end_suite(self, suite):
        LOGGER.end_suite(suite)

    def start_test(self, test):
        LOGGER.start_test(test)

    def end_test(self, test):
        LOGGER.end_test(test)

    def start_keyword(self, kw):
        LOGGER.start_keyword(kw)

    def end_keyword(self, kw):
        LOGGER.end_keyword(kw)

    def message(self, msg):
        LOGGER.log_message(msg)

    def set_log_level(self, level):
        # TODO: Module structure should be cleaned up to prevent cyclic imports
        from .pyloggingconf import set_level
        set_level(level)
        return self._xmllogger.set_log_level(level)

