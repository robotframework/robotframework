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
using logger named ``RobotFramework``.

Log levels
----------

It is possible to log messages using levels ``TRACE``, ``DEBUG``, ``INFO``,
``WARN`` and ``ERROR`` either using the :func:`write` function or, more
commonly, with the log level specific :func:`trace`, :func:`debug`,
:func:`info`, :func:`warn`, :func:`error` functions. The support for the
error level and function is new in RF 2.9.

By default the trace and debug messages are not logged but that can be
changed with the ``--loglevel`` command line option. Warnings and errors are
automatically written also to the console and to the *Test Execution Errors*
section in the log file.

Logging HTML
------------

All methods that are used for writing messages to the log file have an
optional ``html`` argument. If a message to be logged is supposed to be
shown as HTML, this argument should be set to ``True``. Alternatively,
:func:`write` accepts a pseudo log level ``HTML``.

Example
-------

::

    from robot.api import logger

    def my_keyword(arg):
        logger.debug('Got argument %s.' % arg)
        do_something()
        logger.info('<i>This</i> is a boring example.', html=True)
"""

import logging

from robot.output import librarylogger
from robot.running.context import EXECUTION_CONTEXTS


def write(msg, level='INFO', html=False):
    """Writes the message to the log file using the given level.

    Valid log levels are ``TRACE``, ``DEBUG``, ``INFO`` (default since RF
    2.9.1), ``WARN``, and ``ERROR`` (new in RF 2.9). Additionally it is
    possible to use ``HTML`` pseudo log level that logs the message as HTML
    using the ``INFO`` level.

    Instead of using this method, it is generally better to use the level
    specific methods such as ``info`` and ``debug`` that have separate
    ``html`` argument to control the message format.
    """
    if EXECUTION_CONTEXTS.current is not None:
        librarylogger.write(msg, level, html)
    else:
        logger = logging.getLogger("RobotFramework")
        level = {'TRACE': logging.DEBUG // 2,
                 'DEBUG': logging.DEBUG,
                 'INFO': logging.INFO,
                 'HTML': logging.INFO,
                 'WARN': logging.WARN,
                 'ERROR': logging.ERROR}[level]
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


def error(msg, html=False):
    """Writes the message to the log file using the ``ERROR`` level.

    New in Robot Framework 2.9.
    """
    write(msg, 'ERROR', html)


def console(msg, newline=True, stream='stdout'):
    """Writes the message to the console.

    If the ``newline`` argument is ``True``, a newline character is
    automatically added to the message.

    By default the message is written to the standard output stream.
    Using the standard error stream is possibly by giving the ``stream``
    argument value ``'stderr'``.
    """
    librarylogger.console(msg, newline, stream)
