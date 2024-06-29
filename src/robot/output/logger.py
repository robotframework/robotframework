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

import threading
from contextlib import contextmanager
import os
from queue import Empty
from queue import SimpleQueue
from threading import Thread

from robot.errors import DataError

from .console import ConsoleOutput
from .filelogger import FileLogger
from .loggerhelper import AbstractLogger
from .stdoutlogsplitter import StdoutLogSplitter


def start_body_item(method):
    def wrapper(self, *args):
        self._started_keywords += 1
        method(self, *args)
    return wrapper


def end_body_item(method):
    def wrapper(self, *args):
        self._started_keywords -= 1
        method(self, *args)
    return wrapper


def enqueue_action(method=None, wait_until_done=False):
    def enqueue_action_wrapper(method):
        def wrapper(self, *args, **kwargs):
            if threading.current_thread() == self.log_messages_task:
                method(self, *args, **kwargs)
                return
            message_for_queue = MessageQueue(lambda: method(self, *args, **kwargs), wait_until_done)
            self.messages_queue.put(message_for_queue)
            message_for_queue.wait_finish()
        return wrapper
    return enqueue_action_wrapper(method) if callable(method) else enqueue_action_wrapper


class MessageQueue(object):
    def __init__(self, action, wait_until_done=False):
        self.action = action
        self.event = threading.Event() if wait_until_done else None

    def process(self):
        self.action()
        if self.event:
            self.event.set()

    def wait_finish(self):
        if self.event:
            self.event.wait()


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
        self._started_keywords = 0
        self._error_occurred = False
        self._error_listener = None
        self._library_import_logging = False
        self._enabled = 0
        self.closed = False
        self._cache_only = False
        self.messages_queue = SimpleQueue()
        self.log_messages_task = Thread(target=self.log_messages_task_function)
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
        self._enabled += 1
        if self._enabled == 1:
            self.log_messages_task.start()
            self.register_syslog()

    def __exit__(self, *exc_info):
        self._enabled -= 1
        if not self._enabled:
            self.close()
            self.__init__(register_console_logger=False)

    @enqueue_action
    def register_console_logger(self, type='verbose', width=78, colors='AUTO',
                                markers='AUTO', stdout=None, stderr=None):
        logger = ConsoleOutput(type, width, colors, markers, stdout, stderr)
        self._console_logger = self._wrap_and_relay(logger)

    def _wrap_and_relay(self, logger):
        self._relay_cached_messages(logger)
        return logger

    def _relay_cached_messages(self, logger):
        if self._message_cache:
            for msg in self._message_cache[:]:
                logger.message(msg)

    @enqueue_action
    def unregister_console_logger(self):
        self._console_logger = None

    @enqueue_action
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

    @enqueue_action
    def register_xml_logger(self, logger):
        self._xml_logger = self._wrap_and_relay(logger)

    @enqueue_action(wait_until_done=True)
    def unregister_xml_logger(self, callback):
        callback()
        self._xml_logger = None

    @enqueue_action
    def register_listeners(self, listeners, library_listeners):
        self._listeners = listeners
        self._library_listeners = library_listeners
        if listeners:
            self._relay_cached_messages(listeners)

    @enqueue_action
    def register_logger(self, *loggers):
        for logger in loggers:
            logger = self._wrap_and_relay(logger)
            self._other_loggers.append(logger)

    @enqueue_action
    def unregister_logger(self, *loggers):
        for logger in loggers:
            self._other_loggers = [l for l in self._other_loggers if l is not logger]

    @enqueue_action
    def disable_message_cache(self):
        self._message_cache = None

    @enqueue_action
    def register_error_listener(self, listener):
        self._error_listener = listener
        if self._error_occurred:
            listener()

    @enqueue_action
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

    @enqueue_action
    def log_message(self, msg):
        """Log messages written (mainly) by libraries."""
        if self._started_keywords == 0 or self._library_import_logging:
            self.message(msg)
            return

        for logger in self:
            logger.log_message(msg)
        if msg.level in ('WARN', 'ERROR'):
            self.message(msg)

    @enqueue_action
    def log_output(self, output):
        for msg in StdoutLogSplitter(output):
            self.log_message(msg)

    @enqueue_action
    def enable_library_import_logging(self):
        self._library_import_logging = True

    @enqueue_action
    def disable_library_import_logging(self):
        self._library_import_logging = False

    @enqueue_action
    def start_suite(self, data, result):
        for logger in self.start_loggers:
            logger.start_suite(data, result)

    @enqueue_action
    def end_suite(self, data, result):
        for logger in self.end_loggers:
            logger.end_suite(data, result)

    @enqueue_action
    def start_test(self, data, result):
        for logger in self.start_loggers:
            logger.start_test(data, result)

    @enqueue_action
    def end_test(self, data, result):
        for logger in self.end_loggers:
            logger.end_test(data, result)

    @enqueue_action
    @start_body_item
    def start_keyword(self, data, result):
        for logger in self.start_loggers:
            logger.start_keyword(data, result)

    @enqueue_action
    @end_body_item
    def end_keyword(self, data, result):
        for logger in self.end_loggers:
            logger.end_keyword(data, result)

    @enqueue_action
    @start_body_item
    def start_user_keyword(self, data, implementation, result):
        for logger in self.start_loggers:
            logger.start_user_keyword(data, implementation, result)

    @enqueue_action
    @end_body_item
    def end_user_keyword(self, data, implementation, result):
        for logger in self.end_loggers:
            logger.end_user_keyword(data, implementation, result)

    @enqueue_action
    @start_body_item
    def start_library_keyword(self, data, implementation, result):
        for logger in self.start_loggers:
            logger.start_library_keyword(data, implementation, result)

    @enqueue_action
    @end_body_item
    def end_library_keyword(self, data, implementation, result):
        for logger in self.end_loggers:
            logger.end_library_keyword(data, implementation, result)

    @enqueue_action
    @start_body_item
    def start_invalid_keyword(self, data, implementation, result):
        for logger in self.start_loggers:
            logger.start_invalid_keyword(data, implementation, result)

    @enqueue_action
    @end_body_item
    def end_invalid_keyword(self, data, implementation, result):
        for logger in self.end_loggers:
            logger.end_invalid_keyword(data, implementation, result)

    @enqueue_action
    @start_body_item
    def start_for(self, data, result):
        for logger in self.start_loggers:
            logger.start_for(data, result)

    @enqueue_action
    @end_body_item
    def end_for(self, data, result):
        for logger in self.end_loggers:
            logger.end_for(data, result)

    @enqueue_action
    @start_body_item
    def start_for_iteration(self, data, result):
        for logger in self.start_loggers:
            logger.start_for_iteration(data, result)

    @enqueue_action
    @end_body_item
    def end_for_iteration(self, data, result):
        for logger in self.end_loggers:
            logger.end_for_iteration(data, result)

    @enqueue_action
    @start_body_item
    def start_while(self, data, result):
        for logger in self.start_loggers:
            logger.start_while(data, result)

    @enqueue_action
    @end_body_item
    def end_while(self, data, result):
        for logger in self.end_loggers:
            logger.end_while(data, result)

    @enqueue_action
    @start_body_item
    def start_while_iteration(self, data, result):
        for logger in self.start_loggers:
            logger.start_while_iteration(data, result)

    @enqueue_action
    @end_body_item
    def end_while_iteration(self, data, result):
        for logger in self.end_loggers:
            logger.end_while_iteration(data, result)

    @enqueue_action
    @start_body_item
    def start_if(self, data, result):
        for logger in self.start_loggers:
            logger.start_if(data, result)

    @enqueue_action
    @end_body_item
    def end_if(self, data, result):
        for logger in self.end_loggers:
            logger.end_if(data, result)

    @enqueue_action
    @start_body_item
    def start_if_branch(self, data, result):
        for logger in self.start_loggers:
            logger.start_if_branch(data, result)

    @enqueue_action
    @end_body_item
    def end_if_branch(self, data, result):
        for logger in self.end_loggers:
            logger.end_if_branch(data, result)

    @enqueue_action
    @start_body_item
    def start_try(self, data, result):
        for logger in self.start_loggers:
            logger.start_try(data, result)

    @enqueue_action
    @end_body_item
    def end_try(self, data, result):
        for logger in self.end_loggers:
            logger.end_try(data, result)

    @enqueue_action
    @start_body_item
    def start_try_branch(self, data, result):
        for logger in self.start_loggers:
            logger.start_try_branch(data, result)

    @enqueue_action
    @end_body_item
    def end_try_branch(self, data, result):
        for logger in self.end_loggers:
            logger.end_try_branch(data, result)

    @enqueue_action
    @start_body_item
    def start_var(self, data, result):
        for logger in self.start_loggers:
            logger.start_var(data, result)

    @enqueue_action
    @end_body_item
    def end_var(self, data, result):
        for logger in self.end_loggers:
            logger.end_var(data, result)

    @enqueue_action
    @start_body_item
    def start_break(self, data, result):
        for logger in self.start_loggers:
            logger.start_break(data, result)

    @enqueue_action
    @end_body_item
    def end_break(self, data, result):
        for logger in self.end_loggers:
            logger.end_break(data, result)

    @enqueue_action
    @start_body_item
    def start_continue(self, data, result):
        for logger in self.start_loggers:
            logger.start_continue(data, result)

    @enqueue_action
    @end_body_item
    def end_continue(self, data, result):
        for logger in self.end_loggers:
            logger.end_continue(data, result)

    @enqueue_action
    @start_body_item
    def start_return(self, data, result):
        for logger in self.start_loggers:
            logger.start_return(data, result)

    @enqueue_action
    @end_body_item
    def end_return(self, data, result):
        for logger in self.end_loggers:
            logger.end_return(data, result)

    @enqueue_action
    @start_body_item
    def start_error(self, data, result):
        for logger in self.start_loggers:
            logger.start_error(data, result)

    @enqueue_action
    @end_body_item
    def end_error(self, data, result):
        for logger in self.end_loggers:
            logger.end_error(data, result)

    @enqueue_action
    def imported(self, import_type, name, **attrs):
        for logger in self:
            logger.imported(import_type, name, attrs)

    @enqueue_action
    def output_file(self, path):
        for logger in self:
            logger.output_file(path)

    @enqueue_action
    def report_file(self, path):
        for logger in self:
            logger.report_file(path)

    @enqueue_action
    def log_file(self, path):
        for logger in self:
            logger.log_file(path)

    @enqueue_action
    def xunit_file(self, path):
        for logger in self:
            logger.xunit_file(path)

    @enqueue_action
    def debug_file(self, path):
        for logger in self:
            logger.debug_file(path)

    @enqueue_action
    def result_file(self, kind, path):
        kind_file = getattr(self, f'{kind.lower()}_file')
        kind_file(path)

    def close(self):
        self._close()
        self.log_messages_task.join()

    @enqueue_action
    def _close(self):
        for logger in self:
            logger.close()
        self.closed = True

    def log_messages_task_function(self):
        while self.closed is False:
            queued_message = self._pull_messages_from_queue(timeout=1)
            if queued_message is None:
                continue
            queued_message.process()

    def _pull_messages_from_queue(self, timeout):
        try:
            return self.messages_queue.get(timeout=timeout)
        except Empty:
            return None


LOGGER = Logger()
