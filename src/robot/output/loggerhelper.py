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

from robot import utils
from robot.errors import DataError
from robot.model import Message as BaseMessage


LEVELS = {
  'NONE'  : 6,
  'ERROR' : 5,
  'FAIL'  : 4,
  'WARN'  : 3,
  'INFO'  : 2,
  'DEBUG' : 1,
  'TRACE' : 0,
}


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

    def error(self, msg):
        self.write(msg, 'ERROR')

    def write(self, message, level, html=False):
        self.message(Message(message, level, html))

    def message(self, msg):
        raise NotImplementedError(self.__class__)


class Message(BaseMessage):
    __slots__ = ['_message']

    def __init__(self, message, level='INFO', html=False, timestamp=None):
        message = self._normalize_message(message)
        level, html = self._get_level_and_html(level, html)
        timestamp = timestamp or utils.get_timestamp()
        BaseMessage.__init__(self, message, level, html, timestamp)

    def _normalize_message(self, msg):
        if callable(msg):
            return msg
        if not isinstance(msg, unicode):
            msg = utils.unic(msg)
        if '\r\n' in msg:
            msg = msg.replace('\r\n', '\n')
        return msg

    def _get_level_and_html(self, level, html):
        level = level.upper()
        if level == 'HTML':
            return 'INFO', True
        if level not in LEVELS:
            raise DataError("Invalid log level '%s'" % level)
        return level, html

    def _get_message(self):
        if callable(self._message):
            self._message = self._message()
        return self._message

    def _set_message(self, message):
        self._message = message

    message = property(_get_message, _set_message)


class IsLogged:

    def __init__(self, level):
        self._str_level = level
        self._int_level = self._level_to_int(level)

    def __call__(self, level):
        return self._level_to_int(level) >= self._int_level

    def set_level(self, level):
        old = self._str_level.upper()
        self.__init__(level)
        return old

    def _level_to_int(self, level):
        try:
            return LEVELS[level.upper()]
        except KeyError:
            raise DataError("Invalid log level '%s'" % level)


class AbstractLoggerProxy:
    _methods = NotImplemented
    _no_method = lambda *args: None

    def __init__(self, logger):
        self.logger = logger
        for name in self._methods:
            setattr(self, name, self._get_method(logger, name))

    def _get_method(self, logger, name):
        for method_name in self._get_method_names(name):
            if hasattr(logger, method_name):
                return getattr(logger, method_name)
        return self._no_method

    def _get_method_names(self, name):
        return [name, self._toCamelCase(name)]

    def _toCamelCase(self, name):
        parts = name.split('_')
        return ''.join([parts[0]] + [part.capitalize() for part in parts[1:]])
