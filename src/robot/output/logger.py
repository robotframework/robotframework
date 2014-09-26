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

import os

from robot.errors import DataError

from .filelogger import FileLogger
from .loggerhelper import AbstractLogger, AbstractLoggerProxy
from .monitor import CommandLineMonitor
from .stdoutlogsplitter import StdoutLogSplitter


class Logger(AbstractLogger):
    """A global logger proxy to which new loggers may be registered.

    Whenever something is written to LOGGER in code, all registered loggers are
    notified.  Messages are also cached and cached messages written to new
    loggers when they are registered.

    Tools using Robot Framework's internal modules should register their own
    loggers at least to get notifications about errors and warnings. A shortcut
    to get errors/warnings into console is using 'register_console_logger'.
    """

    def __init__(self, register_console_logger=True):
        self._loggers = LoggerCollection()
        self._message_cache = []
        self._console_logger = None
        self._started_keywords = 0
        self._error_occurred = False
        self._error_listener = None
        if register_console_logger:
            self.register_console_logger()

    def disable_message_cache(self):
        self._message_cache = None

    def register_logger(self, *loggers):
        for log in loggers:
            logger = self._loggers.register_regular_logger(log)
            self._relay_cached_messages_to(logger)

    def register_context_changing_logger(self, logger):
        log = self._loggers.register_context_changing_logger(logger)
        self._relay_cached_messages_to(log)

    def _relay_cached_messages_to(self, logger):
        if self._message_cache:
            for msg in self._message_cache[:]:
                logger.message(msg)

    def unregister_logger(self, *loggers):
        for log in loggers:
            self._loggers.unregister_logger(log)

    def register_console_logger(self, width=78, colors='AUTO', markers='AUTO',
                                stdout=None, stderr=None):
        logger = CommandLineMonitor(width, colors, markers, stdout, stderr)
        if self._console_logger:
            self._loggers.unregister_logger(self._console_logger)
        self._console_logger = logger
        self._loggers.register_regular_logger(logger)

    def unregister_console_logger(self):
        if not self._console_logger:
            return None
        logger = self._console_logger
        self._loggers.unregister_logger(logger)
        self._console_logger = None
        return logger

    # TODO: Remove in RF 2.9. Not used outside utests since 2.8.4 but may
    # be used by external tools. Need to check that before removal.
    disable_automatic_console_logger = unregister_console_logger

    def register_file_logger(self, path=None, level='INFO'):
        if not path:
            path = os.environ.get('ROBOT_SYSLOG_FILE', 'NONE')
            level = os.environ.get('ROBOT_SYSLOG_LEVEL', level)
        if path.upper() == 'NONE':
            return
        try:
            logger = FileLogger(path, level)
        except DataError, err:
            self.error("Opening syslog file '%s' failed: %s" % (path, unicode(err)))
        else:
            self.register_logger(logger)

    def register_error_listener(self, listener):
        self._error_listener = listener
        if self._error_occurred:
            listener()

    def message(self, msg):
        """Messages about what the framework is doing, warnings, errors, ..."""
        for logger in self._loggers.all_loggers():
            logger.message(msg)
        if self._message_cache is not None:
            self._message_cache.append(msg)
        if msg.level == 'ERROR':
            self._error_occurred = True
            if self._error_listener:
                self._error_listener()

    def _log_message(self, msg):
        """Log messages written (mainly) by libraries"""
        for logger in self._loggers.all_loggers():
            logger.log_message(msg)
        if msg.level == 'WARN':
            self.message(msg)

    log_message = message

    def log_output(self, output):
        for msg in StdoutLogSplitter(output):
            self.log_message(msg)

    def enable_library_import_logging(self):
        self._prev_log_message = self.log_message
        self.log_message = self.message

    def disable_library_import_logging(self):
        self.log_message = self._prev_log_message

    def output_file(self, name, path):
        """Finished output, report, log, debug, or xunit file"""
        for logger in self._loggers.all_loggers():
            logger.output_file(name, path)

    def close(self):
        for logger in self._loggers.all_loggers():
            logger.close()
        self._loggers = LoggerCollection()
        self._message_cache = []

    def start_suite(self, suite):
        for logger in self._loggers.starting_loggers():
            logger.start_suite(suite)

    def end_suite(self, suite):
        for logger in self._loggers.ending_loggers():
            logger.end_suite(suite)

    def start_test(self, test):
        for logger in self._loggers.starting_loggers():
            logger.start_test(test)

    def end_test(self, test):
        for logger in self._loggers.ending_loggers():
            logger.end_test(test)

    def start_keyword(self, keyword):
        self._started_keywords += 1
        self.log_message = self._log_message
        for logger in self._loggers.starting_loggers():
            logger.start_keyword(keyword)

    def end_keyword(self, keyword):
        self._started_keywords -= 1
        for logger in self._loggers.ending_loggers():
            logger.end_keyword(keyword)
        if not self._started_keywords:
            self.log_message = self.message

    def __iter__(self):
        return iter(self._loggers)


class LoggerCollection(object):

    def __init__(self):
        self._regular_loggers = []
        self._context_changing_loggers = []

    def register_regular_logger(self, logger):
        self._regular_loggers.append(_LoggerProxy(logger))
        return self._regular_loggers[-1]

    def register_context_changing_logger(self, logger):
        self._context_changing_loggers.append(_LoggerProxy(logger))
        return self._context_changing_loggers[-1]

    # TODO: Remove in RF 2.9. Doesn't seem to be used anywhere since 2.8.4.
    def remove_first_regular_logger(self):
        return self._regular_loggers.pop(0)

    def unregister_logger(self, logger):
        self._regular_loggers = [proxy for proxy in self._regular_loggers
                                 if proxy.logger is not logger]
        self._context_changing_loggers = [proxy for proxy
                                          in self._context_changing_loggers
                                          if proxy.logger is not logger]

    def starting_loggers(self):
        return self.all_loggers()

    def ending_loggers(self):
        return self._regular_loggers + self._context_changing_loggers

    def all_loggers(self):
        return self._context_changing_loggers + self._regular_loggers

    def __iter__(self):
        return iter(self.all_loggers())


class _LoggerProxy(AbstractLoggerProxy):
    _methods = ['message', 'log_message', 'output_file', 'close',
                'start_suite', 'end_suite', 'start_test', 'end_test',
                'start_keyword', 'end_keyword']


LOGGER = Logger()
