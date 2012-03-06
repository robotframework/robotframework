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

"""Public logging API for test libraries.

This module provides a public API for writing messages to the log file
and the console. Test libraries can use this API like `logger.info('My
message')` instead of logging through the standard output like `print
'*INFO* My message'`. In addition to a programmatic interface being
cleaner to use, this API has a benefit that the log messages have
accurate timestamps.

Log levels
----------

It is possible to log messages using levels `TRACE`, `DEBUG`, `INFO`
and `WARN` either using the `write` method or, more commonly, with the
log level specific `trace`, `debug`, `info` and `warn` methods.

By default the trace and debug messages are not logged but that can be
changed with the `--loglevel` command line option. Warnings are
automatically written also to the `Test Execution Errors` section in
the log file and to the console.

Logging HTML
------------

All methods that are used for writing messages to the log file have an
optional `html` argument. If a message to be logged is supposed to be
shown as HTML, this argument should be set to `True`.

Example
-------

from robot.api import logger

def my_keyword(arg):
    logger.debug('Got argument %s' % arg)
    do_something()
    logger.info('<i>This</i> is a boring example', html=True)
"""

import sys
import threading

from robot.output import LOGGER, Message
from robot.running.timeouts import timeoutthread


LOGGING_THREADS = ('MainThread', timeoutthread.TIMEOUT_THREAD_NAME)


def write(msg, level, html=False):
    """Writes the message to the log file using the given level.

    Valid log levels are `TRACE`, `DEBUG`, `INFO` and `WARN`. Instead
    of using this method, it is generally better to use the level
    specific methods such as `info` and `debug`.
    """
    if threading.currentThread().getName() in LOGGING_THREADS:
        LOGGER.log_message(Message(msg, level, html))

def trace(msg, html=False):
    """Writes the message to the log file with the TRACE level."""
    write(msg, 'TRACE', html)

def debug(msg, html=False):
    """Writes the message to the log file with the DEBUG level."""
    write(msg, 'DEBUG', html)

def info(msg, html=False, also_console=False):
    """Writes the message to the log file with the INFO level.

    If `also_console` argument is set to `True`, the message is written
    both to the log file and to the console.
    """
    write(msg, 'INFO', html)
    if also_console:
        console(msg)

def warn(msg, html=False):
    """Writes the message to the log file with the WARN level."""
    write(msg, 'WARN', html)

def console(msg, newline=True):
    """Writes the message to the console.

    If the `newline` argument is `True`, a newline character is automatically
    added to the message.
    """
    if newline:
        msg += '\n'
    sys.__stdout__.write(msg)
