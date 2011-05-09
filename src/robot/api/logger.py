#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

import sys

from robot.output import LOGGER, Message


def write(msg, level, html=False):
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

def console(msg, newline=True):
    if newline:
        msg += '\n'
    sys.__stdout__.write(msg)
