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

from contextlib import contextmanager
import os

from robot.errors import DataError

from .console import ConsoleOutput
from .filelogger import FileLogger
from .loggerhelper import AbstractLogger, AbstractLoggerProxy
from .stdoutlogsplitter import StdoutLogSplitter


class Logger(AbstractLogger):
    """A global logger proxy to delegating messages to registered loggers.

    Whenever something is written to LOGGER in code, all registered loggers are
    notified.  Messages are also cached and cached messages written to new
    loggers when they are registered.

    NOTE: This API is likely to change in future versions.
    """

    def __init__(self, register_console_logger=True):
        self._console_logger = None
        self._syslog = None
        self._xml_logger = None
        self._listeners = None
        self._library_listeners = None
        self._other_loggers = []
        self._message_cache = []
        self._log_message_cache = None
        self._started_keywords = 0
        self._error_occurred = False
        self._error_listener = None
        self._prev_log_message_handlers = []
        self._enabled = 0
        self._cache_only = False
        if register_console_logger:
            self.register_console_logger()

    @property
    def start_loggers(self):
        loggers = [self._console_logger, self._syslog, self._xml_logger,
                   self._listeners, self._library_listeners]
        return [logger for logger in self._other_loggers + loggers if logger]

    @property
    def end_loggers(self):
        loggers = [self._listeners, self._library_listeners,
                   self._console_logger, self._syslog, self._xml_logger]
        return [logger for logger in loggers + self._other_loggers if logger]

    def __iter__(self):
        return iter(self.end_loggers)

    def __enter__(self):
        if not self._enabled:
            self.register_syslog()
        self._enabled += 1

    def __exit__(self, *exc_info):
        self._enabled -= 1
        if not self._enabled:
            self.close()

    def register_console_logger(self, type='verbose', width=78, colors='AUTO',
                                markers='AUTO', stdout=None, stderr=None):
        logger = ConsoleOutput(type, width, colors, markers, stdout, stderr)
        self._console_logger = self._wrap_and_relay(logger)

    def _wrap_and_relay(self, logger):
        logger = LoggerProxy(logger)
        self._relay_cached_messages(logger)
        return logger

    def _relay_cached_messages(self, logger):
        if self._message_cache:
            for msg in self._message_cache[:]:
                logger.message(msg)

    def unregister_console_logger(self):
        self._console_logger = None

    def register_syslog(self, path=None, level='INFO'):
        if not path:
            path = os.environ.get('ROBOT_SYSLOG_FILE', 'NONE')
            level = os.environ.get('ROBOT_SYSLOG_LEVEL', level)
        if path.upper() == 'NONE':
            return
        try:
            syslog = FileLogger(path, level)
        except DataError as err:
            self.error("Opening syslog file '%s' failed: %s" % (path, err.message))
        else:
            self._syslog = self._wrap_and_relay(syslog)

    def register_xml_logger(self, logger):
        self._xml_logger = self._wrap_and_relay(logger)

    def unregister_xml_logger(self):
        self._xml_logger = None

    def register_listeners(self, listeners, library_listeners):
        self._listeners = listeners
        self._library_listeners = library_listeners
        if listeners:
            self._relay_cached_messages(listeners)

    def register_logger(self, *loggers):
        for logger in loggers:
            logger = self._wrap_and_relay(logger)
            self._other_loggers.append(logger)

    def unregister_logger(self, *loggers):
        for logger in loggers:
            self._other_loggers = [proxy for proxy in self._other_loggers
                                   if proxy.logger is not logger]

    def disable_message_cache(self):
        self._message_cache = None

    def register_error_listener(self, listener):
        self._error_listener = listener
        if self._error_occurred:
            listener()

    def message(self, msg):
        """Messages about what the framework is doing, warnings, errors, ..."""
        if not self._cache_only:
            for logger in self:
                logger.message(msg)
        if self._message_cache is not None:
            self._message_cache.append(msg)
        if msg.level == 'ERROR':
            self._error_occurred = True
            if self._error_listener:
                self._error_listener()

    @property
    @contextmanager
    def cache_only(self):
        self._cache_only = True
        try:
            yield
        finally:
            self._cache_only = False

    @property
    @contextmanager
    def delayed_logging(self):
        prev_cache = self._log_message_cache
        self._log_message_cache = []
        try:
            yield
        finally:
            messages = self._log_message_cache
            self._log_message_cache = prev_cache
            for msg in messages or ():
                self._log_message(msg, no_cache=True)

    def _log_message(self, msg, no_cache=False):
        """Log messages written (mainly) by libraries."""
        if self._log_message_cache is not None and not no_cache:
            msg.resolve_delayed_message()
            self._log_message_cache.append(msg)
            return
        for logger in self:
            logger.log_message(msg)
        if msg.level in ('WARN', 'ERROR'):
            self.message(msg)

    log_message = message

    def log_output(self, output):
        for msg in StdoutLogSplitter(output):
            self.log_message(msg)

    def enable_library_import_logging(self):
        self._prev_log_message_handlers.append(self.log_message)
        self.log_message = self.message

    def disable_library_import_logging(self):
        self.log_message = self._prev_log_message_handlers.pop()

    def start_suite(self, suite):
        for logger in self.start_loggers:
            logger.start_suite(suite)

    def end_suite(self, suite):
        for logger in self.end_loggers:
            logger.end_suite(suite)

    def start_test(self, test):
        for logger in self.start_loggers:
            logger.start_test(test)

    def end_test(self, test):
        for logger in self.end_loggers:
            logger.end_test(test)

    def start_keyword(self, keyword):
        # TODO: Could _prev_log_message_handlers be used also here?
        self._started_keywords += 1
        self.log_message = self._log_message
        for logger in self.start_loggers:
            logger.start_keyword(keyword)

    def end_keyword(self, keyword):
        self._started_keywords -= 1
        for logger in self.end_loggers:
            logger.end_keyword(keyword)
        if not self._started_keywords:
            self.log_message = self.message

    def imported(self, import_type, name, **attrs):
        for logger in self:
            logger.imported(import_type, name, attrs)

    def output_file(self, file_type, path):
        """Finished output, report, log, debug, or xunit file"""
        for logger in self:
            logger.output_file(file_type, path)

    def close(self):
        for logger in self:
            logger.close()
        self.__init__(register_console_logger=False)


class LoggerProxy(AbstractLoggerProxy):
    _methods = ('start_suite', 'end_suite', 'start_test', 'end_test',
                'start_keyword', 'end_keyword', 'message', 'log_message',
                'imported', 'output_file', 'close')

    _start_keyword_methods = {
        'For': 'start_for',
        'ForIteration': 'start_for_iteration',
        'While': 'start_while',
        'WhileIteration': 'start_while_iteration',
        'If': 'start_if',
        'IfBranch': 'start_if_branch',
        'Try': 'start_try',
        'TryBranch': 'start_try_branch',
        'Return': 'start_return',
        'Continue': 'start_continue',
        'Break': 'start_break',
        'Error': 'start_error'
    }
    _end_keyword_methods = {
        'For': 'end_for',
        'ForIteration': 'end_for_iteration',
        'While': 'end_while',
        'WhileIteration': 'end_while_iteration',
        'If': 'end_if',
        'IfBranch': 'end_if_branch',
        'Try': 'end_try',
        'TryBranch': 'end_try_branch',
        'Return': 'end_return',
        'Continue': 'end_continue',
        'Break': 'end_break',
        'Error': 'end_error'
    }

    def start_keyword(self, kw):
        # Dispatch start_keyword calls to more precise methods when logger
        # implements them. This horrible hack is needed because internal logger
        # knows only about keywords. It should be rewritten.
        name = self._start_keyword_methods.get(type(kw.result).__name__)
        if name and hasattr(self.logger, name):
            method = getattr(self.logger, name)
        else:
            method = self.logger.start_keyword
        method(kw)

    def end_keyword(self, kw):
        # See start_keyword comment for explanation of this horrible hack.
        name = self._end_keyword_methods.get(type(kw.result).__name__)
        if name and hasattr(self.logger, name):
            method = getattr(self.logger, name)
        else:
            method = self.logger.end_keyword
        method(kw)


LOGGER = Logger()
