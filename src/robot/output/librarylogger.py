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

"""Implementation of the public test library logging API.

This is exposed via :py:mod:`robot.api.logger`. Implementation must reside
here to avoid cyclic imports.
"""

import sys
import threading

from robot.utils import unic, encode_output

from .logger import LOGGER
from .loggerhelper import Message


LOGGING_THREADS = ('MainThread', 'RobotFrameworkTimeoutThread')


def write(msg, level, html=False):
    # Callable messages allow lazy logging internally, but we don't want to
    # expose this functionality publicly. See the following issue for details:
    # http://code.google.com/p/robotframework/issues/detail?id=1505
    if callable(msg):
        msg = unic(msg)
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


def console(msg, newline=True, stream='stdout'):
    msg = unic(msg)
    if newline:
        msg += '\n'
    stream = sys.__stdout__ if stream.lower() != 'stderr' else sys.__stderr__
    stream.write(encode_output(msg))
    stream.flush()
