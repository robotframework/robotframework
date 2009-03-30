#  Copyright 2008 Nokia Siemens Networks Oyj
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

from robot import utils

from loggerhelper import AbstractLogger, Message
from filelogger import FileLogger
from monitor import CommandLineMonitor


class _Logger(AbstractLogger):
    """A global logger proxy to which new loggers may be registered.

    Whenever something is written to LOGGER in code, all registered loggers are
    notified.  Messages are also cached and cached messages written to new
    loggers when they are registered.

    Tools using Robot Framework's internal modules should register their own
    loggers at least to get notifications about errors and warnings. A shortcut
    to get errors/warnings into console is using 'register_console_logger'.
    """

    def __init__(self):
        self._loggers = []
        self._message_cache = []
        self._register_console_logger()
        self._console_logger_disabled = False

    def disable_message_cache(self):
        self._message_cache = None

    def disable_automatic_console_logger(self):
        if self._console_logger_disabled:
            raise TypeError('Automatic console logging has already been disabled')
        self._loggers.pop(0)
        self._console_logger_disabled = True

    def register_logger(self, *loggers):
        for log in loggers:
            logger = _LoggerProxy(log)
            self._loggers.append(logger)
            if self._message_cache:
                for msg in self._message_cache:
                    logger.write(msg, msg.level)

    def register_console_logger(self, width=78, colors=True):
        self.disable_automatic_console_logger()
        self._register_console_logger(width, colors)

    def _register_console_logger(self, width=78, colors=True):
        monitor = CommandLineMonitor(width, colors)
        self.register_logger(monitor)

    def register_file_logger(self, path=None, level='INFO'):
        if not path:
            path = os.environ.get('ROBOT_SYSLOG_FILE', 'NONE')
            level = os.environ.get('ROBOT_SYSLOG_LEVEL', level)
        if path.upper() == 'NONE':
            return
        try:
            logger = FileLogger(path, level)
        except:
            self.error("Opening syslog file '%s' failed: %s"  
                       % (path, utils.get_error_message()))
        else:
            self.register_logger(logger)

    def write(self, message, level='INFO'):
        """Messages about what the framework is doing, warnings, errors, ..."""
        self._write(Message(message, level))

    def _write(self, msg):
        for logger in self._loggers:
            logger.write(msg, msg.level)   # TODO: Pass only msg?
        if self._message_cache is not None:
            self._message_cache.append(msg)

    def log_message(self, msg):
        """Log messages written (mainly) by libraries"""
        for logger in self._loggers:
            logger.log_message(msg)
        if msg.level == 'WARN':
            self._write(msg)
        
    def output_file(self, name, path):
        """Finished output, report, log, summary or debug file (incl. split)"""
        for logger in self._loggers:
            logger.output_file(name, path)

    def close(self):
        for logger in self._loggers:
            logger.close()
        self._loggers = []
        self._message_cache = []

    def start_suite(self, suite):
        for logger in self._loggers:
            logger.start_suite(suite)

    def end_suite(self, suite):
        for logger in self._loggers:
            logger.end_suite(suite)

    def start_test(self, test):
        for logger in self._loggers:
            logger.start_test(test)

    def end_test(self, test):
        for logger in self._loggers:
            logger.end_test(test)

    def start_keyword(self, keyword):
        for logger in self._loggers:
            logger.start_keyword(keyword)

    def end_keyword(self, keyword):
        for logger in self._loggers:
            logger.end_keyword(keyword)


class _LoggerProxy:

    def __init__(self, logger):
        default = lambda *args: None
        for name in ['write', 'log_message', 'output_file', 'close',
                     'start_suite', 'end_suite', 'start_test', 'end_test',
                     'start_keyword', 'end_keyword']:
            method = getattr(logger, name, default)
            setattr(self, name, method)


LOGGER = _Logger()
