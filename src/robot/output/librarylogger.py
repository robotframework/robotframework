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

"""Implementation of the public test library logging API.

This is exposed via :py:mod:`robot.api.logger`. Implementation must reside
here to avoid cyclic imports.
"""

import sys
import threading

from robot.errors import DataError
from robot.utils import unic, console_encode

from .logger import LOGGER
from .loggerhelper import Message


LOGGING_THREADS = ('MainThread', 'RobotFrameworkTimeoutThread')


def write(msg, level, html=False):
    # Callable messages allow lazy logging internally, but we don't want to
    # expose this functionality publicly. See the following issue for details:
    # https://github.com/robotframework/robotframework/issues/1505
    if callable(msg):
        msg = unic(msg)
    if level.upper() not in ('TRACE', 'DEBUG', 'INFO', 'HTML', 'WARN', 'ERROR'):
        raise DataError("Invalid log level '%s'." % level)
    if threading.currentThread().getName() in LOGGING_THREADS:
        LOGGER.log_message(Message(msg, level, html))


def trace(msg, html=False):
    write(msg, 'TRACE', html)


def debug(msg, html=False):
    write(msg, 'DEBUG', html)


def info(msg, html=False, also_console=False):
    write(msg, 'INFO', html)
    if also_console:
        console(msg)


def warn(msg, html=False):
    write(msg, 'WARN', html)


def error(msg, html=False):
    write(msg, 'ERROR', html)


def console(msg, newline=True, stream='stdout'):
    msg = unic(msg)
    if newline:
        msg += '\n'
    stream = sys.__stdout__ if stream.lower() != 'stderr' else sys.__stderr__
    stream.write(console_encode(msg, stream=stream))
    stream.flush()
