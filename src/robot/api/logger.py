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

    print('*INFO* My message')

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
:func:`info`, :func:`warn`, :func:`error` functions.

The trace and debug messages are not logged by default, but that can be
changed with the ``--loglevel`` command line option. Warnings and errors are
automatically written also to the console and to the *Test Execution Errors*
section in the log file.

If libraries accept arbitrary log levels and use type hints, they can use
the :attr:`LogLevel` type alias as shown in the example_ below. It is new
in Robot Framework 7.4, but :attr:`LOGLEVEL` with same content exists since
Robot Framework 7.0 and will be available at least until in Robot Framework 9.0.

Logging HTML
------------

All methods that are used for writing messages to the log file have an
optional ``html`` argument. If a message to be logged is supposed to be
shown as HTML, this argument should be set to ``True``. Alternatively,
:func:`write` accepts a pseudo log level ``HTML``.

Logging to console
------------------

Normal messages are written only to the log file, not to the console.
There are, however, various ways to log to the console if needed:

- Messages with ``WARN`` and ``ERROR`` levels are shown on the console automatically.
- The :func:`console` function logs only to the console.
- The :func:`info` function supports logging both to the log file and to
  the console by using the ``also_console`` argument.
- The :func:`write` function supports a pseudo log level ``CONSOLE`` that
  can be used for logging both the log file and to the console.

Example
-------

::

    from robot.api import logger


    def my_keyword(arg: str):
        logger.debug(f"Got argument {arg}.")
        logger.info("<b>Robot Framework</b> rocks!", html=True)


    def another_keyword(arg: int, log_level: logger.LogLevel = "INFO"):
        logger.write(f"Got argument {arg}.", log_level)
"""

import logging
from typing import Literal

from robot.output import librarylogger
from robot.running.context import EXECUTION_CONTEXTS

# LOGLEVEL was introduced in RF 7.0 and naming convention compliant LogLevel in RF 7.4.
# TODO: Deprecate LOGLEVEL in RF 8.0. Update the above "Log levels" section as well.
LogLevel = Literal["TRACE", "DEBUG", "INFO", "CONSOLE", "HTML", "WARN", "ERROR"]
LOGLEVEL = LogLevel


def write(
    msg: object,
    level: LogLevel = "INFO",
    html: bool = False,
    console: "bool | None" = None,
):
    """Writes the message to the log file using the specified level.

    :param msg: The message to be logged. Converted to string automatically.
    :param level: Either the actual log level to use or a pseudo log level
        ``HTML`` or ``CONSOLE``.
    :param html: When set to ``True``, the message is considered to be HTML.
    :param console:  Controls writing the message to the console in addition
        to the log file. If ``None`` (default), messages with the ``ERROR`` and
        ``WARN`` level are written to the console and others are not.

    Valid log levels are ``TRACE``, ``DEBUG``, ``INFO`` (default), ``WARN``,
    and ``ERROR``. In addition to that, there are pseudo log levels ``HTML``
    and ``CONSOLE`` for logging messages as HTML and for logging messages
    both to the log file and to the console, respectively. With both of these
    pseudo levels the level in the log file will be ``INFO``.

    Instead of using this method, it is generally better to use the level
    specific methods such as ``info`` and ``debug``.

    The ``CONSOLE`` pseudo level is new in Robot Framework 6.1 and
    the ``console`` argument is new in Robot Framework 7.4.
    """
    if EXECUTION_CONTEXTS.current is not None:
        librarylogger.write(msg, level, html, console)
    else:
        logger = logging.getLogger("RobotFramework")
        level_int = {
            "TRACE": logging.DEBUG // 2,
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "CONSOLE": logging.INFO,
            "HTML": logging.INFO,
            "WARN": logging.WARNING,
            "ERROR": logging.ERROR,
        }[level]
        logger.log(level_int, msg)


def trace(msg: object, html: bool = False):
    """Writes the message to the log file using the ``TRACE`` level.

    :param msg: The message to be logged. Converted to string automatically.
    :param html: When set to ``True``, the message is considered to be HTML.
    """
    write(msg, "TRACE", html)


def debug(msg: object, html: bool = False):
    """Writes the message to the log file using the ``DEBUG`` level.

    :param msg: The message to be logged. Converted to string automatically.
    :param html: When set to ``True``, the message is considered to be HTML.
    """
    write(msg, "DEBUG", html)


def info(
    msg: object,
    html: bool = False,
    also_console: bool = False,
    console: bool = False,
):
    """Writes the message to the log file using the ``INFO`` level.

    :param msg: The message to be logged. Converted to string automatically.
    :param html: When set to ``True``, the message is considered to be HTML.
    :param also_console: Deprecated alias for ``console``.
    :param console: When ``True``, the message is logged to the console in
        addition to the log file.

    The ``console`` argument was introduced in Robot Framework 7.4 as
    a replacement for the older ``also_console`` argument. Both are supported
    for now, but ``also_console`` will be deprecated and removed in the future.
    """
    write(msg, "INFO", html, also_console or console)


def warn(msg: object, html: bool = False, console: bool = True):
    """Writes the message to the log file using the ``WARN`` level.

    :param msg: The message to be logged. Converted to string automatically.
    :param html: When set to ``True``, the message is considered to be HTML.
    :param console: When ``False``, the message is not logged to the console.
        New in Robot Framework 7.4.
    """
    write(msg, "WARN", html, console)


def error(msg: object, html: bool = False, console: bool = True):
    """Writes the message to the log file using the ``ERROR`` level.

    :param msg: The message to be logged. Converted to string automatically.
    :param html: When set to ``True``, the message is considered to be HTML.
    :param console: When ``False``, the message is not logged to the console.
        New in Robot Framework 7.4.
    """
    write(msg, "ERROR", html, console)


def console(
    msg: object,
    newline: bool = True,
    stream: Literal["stdout", "stderr"] = "stdout",
):
    """Writes the message to the console.

    :param msg: The message to be logged. Converted to string automatically.
    :param newline: When ``True``, a newline character is automatically added
        to the message.
    :param stream: Name of the standard stream to write the message to.
    """
    librarylogger.console(msg, newline, stream)
