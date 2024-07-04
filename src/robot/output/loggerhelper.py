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

import sys
from datetime import datetime
from typing import Callable, Literal

from robot.errors import DataError
from robot.model import Message as BaseMessage, MessageLevel
from robot.utils import console_encode, safe_str


LEVELS = {
  'NONE'  : 7,
  'SKIP'  : 6,
  'FAIL'  : 5,
  'ERROR' : 4,
  'WARN'  : 3,
  'INFO'  : 2,
  'DEBUG' : 1,
  'TRACE' : 0,
}
PseudoLevel = Literal['HTML', 'CONSOLE']


def write_to_console(msg, newline=True, stream='stdout'):
    msg = str(msg)
    if newline:
        msg += '\n'
    stream = sys.__stdout__ if stream.lower() != 'stderr' else sys.__stderr__
    stream.write(console_encode(msg, stream=stream))
    stream.flush()


class AbstractLogger:

    def __init__(self, level='TRACE'):
        self._is_logged = IsLogged(level)

    def set_level(self, level):
        return self._is_logged.set_level(level)

    def trace(self, msg):
        self.write(msg, 'TRACE')

    def debug(self, msg):
        self.write(msg, 'DEBUG')

    def info(self, msg):
        self.write(msg, 'INFO')

    def warn(self, msg):
        self.write(msg, 'WARN')

    def fail(self, msg):
        html = False
        if msg.startswith("*HTML*"):
            html = True
            msg = msg[6:].lstrip()
        self.write(msg, 'FAIL', html)

    def skip(self, msg):
        html = False
        if msg.startswith("*HTML*"):
            html = True
            msg = msg[6:].lstrip()
        self.write(msg, 'SKIP', html)

    def error(self, msg):
        self.write(msg, 'ERROR')

    def write(self, message, level, html=False):
        self.message(Message(message, level, html))

    def message(self, msg):
        raise NotImplementedError(self.__class__)


class Message(BaseMessage):
    __slots__ = ['_message']

    def __init__(self, message: 'str|Callable[[], str]',
                 level: 'MessageLevel|PseudoLevel' = 'INFO',
                 html: bool = False,
                 timestamp: 'datetime|str|None' = None):
        level, html = self._get_level_and_html(level, html)
        super().__init__(message, level, html, timestamp or datetime.now())

    def _get_level_and_html(self, level, html) -> 'tuple[MessageLevel, bool]':
        level = level.upper()
        if level == 'HTML':
            return 'INFO', True
        if level == 'CONSOLE':
            return 'INFO', html
        if level in LEVELS:
            return level, html
        raise DataError(f"Invalid log level '{level}'.")

    @property
    def message(self) -> str:
        self.resolve_delayed_message()
        return self._message

    @message.setter
    def message(self, message: 'str|Callable[[], str]'):
        if not callable(message):
            if not isinstance(message, str):
                message = safe_str(message)
            if '\r\n' in message:
                message = message.replace('\r\n', '\n')
        self._message = message

    def resolve_delayed_message(self):
        if callable(self._message):
            self._message = self._message()


class IsLogged:

    def __init__(self, level):
        self.level = level.upper()
        self._int_level = self._level_to_int(level)

    def __call__(self, level):
        return self._level_to_int(level) >= self._int_level

    def set_level(self, level):
        old = self.level
        self.__init__(level)
        return old

    @classmethod
    def validate_level(cls, level):
        cls._level_to_int(level)

    @classmethod
    def _level_to_int(cls, level):
        try:
            return LEVELS[level.upper()]
        except KeyError:
            raise DataError("Invalid log level '%s'." % level)
