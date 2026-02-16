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

import os
from contextlib import contextmanager

from robot.errors import DataError

from .console import ConsoleOutput
from .filelogger import FileLogger
from .loggerhelper import AbstractLogger, write_to_console
from .stdoutlogsplitter import StdoutLogSplitter


def start_body_item(method):
    def wrapper(self, *args):
        self._log_message_parents.append(args[-1])
        method(self, *args)

    return wrapper


def end_body_item(method):
    def wrapper(self, *args):
        method(self, *args)
        self._log_message_parents.pop()

    return wrapper


class Logger(AbstractLogger):
    """A global logger proxy to delegating messages to registered loggers.

    Whenever something is written to LOGGER in code, all registered loggers are
    notified.  Messages are also cached and cached messages written to new
    loggers when they are registered.

    NOTE: This is a private API and likely to change in the future.
    """

    def __init__(self, register_console_logger=True):
        self._console = None
        self._syslog = None
        self._output_file = None
        self._cli_listeners = None
        self._lib_listeners = None
        self._other_loggers = []
        self._message_cache = []
        self._log_message_parents = []
        self._library_import_logging = 0
        self._error_occurred = False
        self._error_listener = None
        self._enabled = 0
        self._cache_only = False
        if register_console_logger:
            self.register_console_logger()

    @property
    def _std_loggers(self):
        loggers = (self._console, self._syslog, self._output_file)
        return [lo for lo in loggers if lo]

    @property
    def _listeners(self):
        cli_listeners = tuple(self._cli_listeners or ())
        lib_listeners = tuple(self._lib_listeners or ())
        return sorted(cli_listeners + lib_listeners, key=lambda li: -li.priority)

    @property
    def start_loggers(self):
        return [*self._other_loggers, *self._std_loggers, *self._listeners]

    @property
    def end_loggers(self):
        return [*self._listeners, *self._std_loggers, *self._other_loggers]

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

    def register_console_logger(
        self,
        type="verbose",
        width=78,
        colors="AUTO",
        links="AUTO",
        markers="AUTO",
        stdout=None,
        stderr=None,
    ):
        self._console = ConsoleOutput(
            type, width, colors, links, markers, stdout, stderr
        )
        self._relay_cached_messages(self._console)

    def _relay_cached_messages(self, logger):
        if self._message_cache:
            for msg in self._message_cache[:]:
                logger.message(msg)

    def unregister_console_logger(self):
        self._console = None

    def register_syslog(self, path=None, level="INFO"):
        if not path:
            path = os.environ.get("ROBOT_SYSLOG_FILE", "NONE")
            level = os.environ.get("ROBOT_SYSLOG_LEVEL", level)
        if path.upper() == "NONE":
            return
        try:
            self._syslog = FileLogger(path, level)
        except DataError as err:
            self.error(f"Opening syslog file '{path}' failed: {err}")
        else:
            self._relay_cached_messages(self._syslog)

    def register_output_file(self, logger):
        self._relay_cached_messages(logger)
        self._output_file = logger

    def unregister_output_file(self):
        self._output_file = None

    def register_listeners(self, listeners, library_listeners):
        self._cli_listeners = listeners
        self._lib_listeners = library_listeners
        for listener in listeners or ():
            self._relay_cached_messages(listener)

    def register_logger(self, *loggers):
        for logger in loggers:
            self._relay_cached_messages(logger)
            self._other_loggers.append(logger)

    def unregister_logger(self, *loggers):
        for logger in loggers:
            self._other_loggers = [lo for lo in self._other_loggers if lo is not logger]

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
        if msg.level == "ERROR":
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

    def log_message(self, msg):
        """Log messages written (mainly) by libraries."""
        logged = False
        # Common case. We can log normally.
        if self._log_message_parents and not self._library_import_logging:
            for logger in self:
                logger.log_message(msg)
            if self._output_file and self._output_file.is_logged(msg):
                self._log_message_parents[-1].body.append(msg)
            logged = True
        # Handle warnings and errors as well as logging to console.
        if msg.level in ("WARN", "ERROR"):
            self.message(msg)
            logged = True
        elif msg.console:
            write_to_console(msg.message)
            msg.console = False
        # If not logged otherwise, log as a system message.
        if not logged:
            self.message(msg)

    def log_output(self, output):
        for msg in StdoutLogSplitter(output):
            self.log_message(msg)

    def enable_library_import_logging(self):
        self._library_import_logging += 1

    def disable_library_import_logging(self):
        self._library_import_logging -= 1

    def start_suite(self, data, result):
        for logger in self.start_loggers:
            logger.start_suite(data, result)

    def end_suite(self, data, result):
        for logger in self.end_loggers:
            logger.end_suite(data, result)

    def start_test(self, data, result):
        self._log_message_parents.append(result)
        for logger in self.start_loggers:
            logger.start_test(data, result)

    def end_test(self, data, result):
        for logger in self.end_loggers:
            logger.end_test(data, result)
        self._log_message_parents.pop()

    @start_body_item
    def start_keyword(self, data, result):
        for logger in self.start_loggers:
            logger.start_keyword(data, result)

    @end_body_item
    def end_keyword(self, data, result):
        for logger in self.end_loggers:
            logger.end_keyword(data, result)

    @start_body_item
    def start_user_keyword(self, data, implementation, result):
        for logger in self.start_loggers:
            logger.start_user_keyword(data, implementation, result)

    @end_body_item
    def end_user_keyword(self, data, implementation, result):
        for logger in self.end_loggers:
            logger.end_user_keyword(data, implementation, result)

    @start_body_item
    def start_library_keyword(self, data, implementation, result):
        for logger in self.start_loggers:
            logger.start_library_keyword(data, implementation, result)

    @end_body_item
    def end_library_keyword(self, data, implementation, result):
        for logger in self.end_loggers:
            logger.end_library_keyword(data, implementation, result)

    @start_body_item
    def start_invalid_keyword(self, data, implementation, result):
        for logger in self.start_loggers:
            logger.start_invalid_keyword(data, implementation, result)

    @end_body_item
    def end_invalid_keyword(self, data, implementation, result):
        for logger in self.end_loggers:
            logger.end_invalid_keyword(data, implementation, result)

    @start_body_item
    def start_for(self, data, result):
        for logger in self.start_loggers:
            logger.start_for(data, result)

    @end_body_item
    def end_for(self, data, result):
        for logger in self.end_loggers:
            logger.end_for(data, result)

    @start_body_item
    def start_for_iteration(self, data, result):
        for logger in self.start_loggers:
            logger.start_for_iteration(data, result)

    @end_body_item
    def end_for_iteration(self, data, result):
        for logger in self.end_loggers:
            logger.end_for_iteration(data, result)

    @start_body_item
    def start_while(self, data, result):
        for logger in self.start_loggers:
            logger.start_while(data, result)

    @end_body_item
    def end_while(self, data, result):
        for logger in self.end_loggers:
            logger.end_while(data, result)

    @start_body_item
    def start_while_iteration(self, data, result):
        for logger in self.start_loggers:
            logger.start_while_iteration(data, result)

    @end_body_item
    def end_while_iteration(self, data, result):
        for logger in self.end_loggers:
            logger.end_while_iteration(data, result)

    @start_body_item
    def start_group(self, data, result):
        for logger in self.start_loggers:
            logger.start_group(data, result)

    @end_body_item
    def end_group(self, data, result):
        for logger in self.end_loggers:
            logger.end_group(data, result)

    @start_body_item
    def start_if(self, data, result):
        for logger in self.start_loggers:
            logger.start_if(data, result)

    @end_body_item
    def end_if(self, data, result):
        for logger in self.end_loggers:
            logger.end_if(data, result)

    @start_body_item
    def start_if_branch(self, data, result):
        for logger in self.start_loggers:
            logger.start_if_branch(data, result)

    @end_body_item
    def end_if_branch(self, data, result):
        for logger in self.end_loggers:
            logger.end_if_branch(data, result)

    @start_body_item
    def start_try(self, data, result):
        for logger in self.start_loggers:
            logger.start_try(data, result)

    @end_body_item
    def end_try(self, data, result):
        for logger in self.end_loggers:
            logger.end_try(data, result)

    @start_body_item
    def start_try_branch(self, data, result):
        for logger in self.start_loggers:
            logger.start_try_branch(data, result)

    @end_body_item
    def end_try_branch(self, data, result):
        for logger in self.end_loggers:
            logger.end_try_branch(data, result)

    @start_body_item
    def start_var(self, data, result):
        for logger in self.start_loggers:
            logger.start_var(data, result)

    @end_body_item
    def end_var(self, data, result):
        for logger in self.end_loggers:
            logger.end_var(data, result)

    @start_body_item
    def start_break(self, data, result):
        for logger in self.start_loggers:
            logger.start_break(data, result)

    @end_body_item
    def end_break(self, data, result):
        for logger in self.end_loggers:
            logger.end_break(data, result)

    @start_body_item
    def start_continue(self, data, result):
        for logger in self.start_loggers:
            logger.start_continue(data, result)

    @end_body_item
    def end_continue(self, data, result):
        for logger in self.end_loggers:
            logger.end_continue(data, result)

    @start_body_item
    def start_return(self, data, result):
        for logger in self.start_loggers:
            logger.start_return(data, result)

    @end_body_item
    def end_return(self, data, result):
        for logger in self.end_loggers:
            logger.end_return(data, result)

    @start_body_item
    def start_error(self, data, result):
        for logger in self.start_loggers:
            logger.start_error(data, result)

    @end_body_item
    def end_error(self, data, result):
        for logger in self.end_loggers:
            logger.end_error(data, result)

    def library_import(self, library, importer):
        for logger in self:
            logger.library_import(library, importer)

    def resource_import(self, resource, importer):
        for logger in self:
            logger.resource_import(resource, importer)

    def variables_import(self, variables, importer):
        for logger in self:
            logger.variables_import(variables, importer)

    def output_file(self, path):
        for logger in self:
            logger.output_file(path)

    def report_file(self, path):
        for logger in self:
            logger.report_file(path)

    def log_file(self, path):
        for logger in self:
            logger.log_file(path)

    def xunit_file(self, path):
        for logger in self:
            logger.xunit_file(path)

    def debug_file(self, path):
        for logger in self:
            logger.debug_file(path)

    def result_file(self, kind, path):
        kind_file = getattr(self, f"{kind.lower()}_file")
        kind_file(path)

    def close(self):
        for logger in self:
            logger.close()
        self.__init__(register_console_logger=False)


LOGGER = Logger()
