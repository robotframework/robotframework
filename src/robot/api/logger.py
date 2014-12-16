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

"""Public logging API for test libraries.

This module provides a public API for writing messages to the log file
and the console. Test libraries can use this API like::

    logger.info('My message')

instead of logging through the standard output like::

    print '*INFO* My message'

In addition to a programmatic interface being cleaner to use, this API
has a benefit that the log messages have accurate timestamps.

If the logging methods are used when Robot Framework is not running,
the messages are redirected to the standard Python ``logging`` module
using logger named ``RobotFramework``. This feature was added in RF 2.8.7.

Log levels
----------

It is possible to log messages using levels ``TRACE``, ``DEBUG``, ``INFO``
and ``WARN`` either using the ``write`` method or, more commonly, with the
log level specific ``trace``, ``debug``, ``info`` and ``warn`` methods.

By default the trace and debug messages are not logged but that can be
changed with the ``--loglevel`` command line option. Warnings are
automatically written also to the `Test Execution Errors` section in
the log file and to the console.

Logging HTML
------------

All methods that are used for writing messages to the log file have an
optional ``html`` argument. If a message to be logged is supposed to be
shown as HTML, this argument should be set to ``True``.

Example
-------

::

    from robot.api import logger

    def my_keyword(arg):
        logger.debug('Got argument %s.' % arg)
        do_something()
        logger.info('<i>This</i> is a boring example.', html=True)

Logging from background threads
-------------------------------

``BackgroundLogger`` is a custom logger that works mostly like the
standard ``robot.api.logger`` methods, but also stores messages logged by
background threads. It also provides a method the main thread can use to
forward the logged messages to Robot Framework's log. See below for more
information. ``BackgroundLogger`` is new in RF 2.8.7.
"""

from __future__ import with_statement
import logging
import threading
import time
try:
    from collections import OrderedDict
except ImportError:  # New in 2.7 but 2.4 compatible recipe would be available.
    OrderedDict = dict

from robot.output import librarylogger
from robot.running.context import EXECUTION_CONTEXTS


def write(msg, level, html=False):
    """Writes the message to the log file using the given level.

    Valid log levels are ``TRACE``, ``DEBUG``, ``INFO`` and ``WARN``.
    Instead of using this method, it is generally better to use the level
    specific methods such as ``info`` and ``debug``.
    """
    if EXECUTION_CONTEXTS.current is not None:
        librarylogger.write(msg, level, html)
    else:
        logger = logging.getLogger("RobotFramework")
        level = {'TRACE': logging.DEBUG/2,
                 'DEBUG': logging.DEBUG,
                 'INFO': logging.INFO,
                 'WARN': logging.WARN}[level]
        logger.log(level, msg)


def trace(msg, html=False):
    """Writes the message to the log file using the ``TRACE`` level."""
    write(msg, 'TRACE', html)


def debug(msg, html=False):
    """Writes the message to the log file using the ``DEBUG`` level."""
    write(msg, 'DEBUG', html)


def info(msg, html=False, also_console=False):
    """Writes the message to the log file using the ``INFO`` level.

    If ``also_console`` argument is set to ``True``, the message is
    written both to the log file and to the console.
    """
    write(msg, 'INFO', html)
    if also_console:
        console(msg)


def warn(msg, html=False):
    """Writes the message to the log file using the ``WARN`` level."""
    write(msg, 'WARN', html)


def console(msg, newline=True, stream='stdout'):
    """Writes the message to the console.

    If the ``newline`` argument is ``True``, a newline character is
    automatically added to the message.

    By default the message is written to the standard output stream.
    Using the standard error stream is possibly by giving the ``stream``
    argument value ``'stderr'``. This is a new feature in RF 2.8.2.
    """
    librarylogger.console(msg, newline, stream)


class BaseLogger(object):
    """Base class for custom loggers with same api as ``robot.api.logger``.
    """

    def trace(self, msg, html=False):
        self.write(msg, 'TRACE', html)

    def debug(self, msg, html=False):
        self.write(msg, 'DEBUG', html)

    def info(self, msg, html=False, also_to_console=False):
        self.write(msg, 'INFO', html)
        if also_to_console:
            self.console(msg)

    def warn(self, msg, html=False):
        self.write(msg, 'WARN', html)

    def console(self, msg, newline=True, stream='stdout'):
        console(msg, newline, stream)

    def write(self, msg, level, html=False):
        raise NotImplementedError


class BackgroundLogger(BaseLogger):
    """A logger which can be used from multiple threads. The messages from main
    thread will go to robot logging api (or Python logging if Robot is not running).
    Messages from other threads are saved to memory and can be later logged with
    ``log_background_messages()``. This will also remove the messages from memory.

    Example::

        from robotbackgroundlogger import BackgroundLogger
        logger = BackgroundLogger()

    After that logger can be used mostly like ``robot.api.logger`::

        logger.debug('Hello, world!')
        logger.info('<b>HTML</b> example', html=True)
    """
    LOGGING_THREADS = librarylogger.LOGGING_THREADS

    def __init__(self):
        self.lock = threading.RLock()
        self._messages = OrderedDict()

    def write(self, msg, level, html=False):
        with self.lock:
            thread = threading.currentThread().getName()
            if thread in self.LOGGING_THREADS:
                write(msg, level, html)
            else:
                message = _BackgroundMessage(msg, level, html)
                self._messages.setdefault(thread, []).append(message)

    def log_background_messages(self, name=None):
        """Forwards messages logged on background to Robot Framework log.

        By default forwards all messages logged by all threads, but can be
        limited to a certain thread by passing thread's name as an argument.
        This method must be called from the main thread.

        Logged messages are removed from the message storage.
        """
        thread = threading.currentThread().getName()
        if thread not in self.LOGGING_THREADS:
            raise RuntimeError("Logging background messages is only allowed from main thread. Current thread name: %s" % thread)
        with self.lock:
            if name:
                self._log_messages_by_thread(name)
            else:
                self._log_all_messages()

    def _log_messages_by_thread(self, name):
        for message in self._messages.pop(name, []):
            print message.format()

    def _log_all_messages(self):
        for thread in list(self._messages):
            # Only way to get custom timestamps currently is with print
            print "*HTML* <b>Messages by '%s'</b>" % thread
            for message in self._messages.pop(thread):
                print message.format()

    def reset_background_messages(self, name=None):
        with self.lock:
            if name:
                self._messages.pop(name)
            else:
                self._messages.clear()


class _BackgroundMessage(object):

    def __init__(self, message, level='INFO', html=False):
        self.message = message
        self.level = level.upper()
        self.html = html
        self.timestamp = time.time() * 1000

    def format(self):
        # Can support HTML logging only with INFO level.
        html = self.html and self.level == 'INFO'
        level = self.level if not html else 'HTML'
        return "*%s:%d* %s" % (level, round(self.timestamp), self.message)
