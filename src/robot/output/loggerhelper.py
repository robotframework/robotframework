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


from robot import utils
from robot.errors import DataError


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
        self.write(msg, 'FAIL')

    def error(self, msg):
        self.write(msg, 'ERROR')

    def write(self, message, level, html=False):
        self.message(Message(message, level, html))

    def message(self, msg):
        raise NotImplementedError(self.__class__)


class Message(object):
    __slots__ = ['level', 'html', 'timestamp', 'linkable', '_setter__message']

    def __init__(self, message, level='INFO', html=False, timestamp=None,
                 linkable=False):
        self.message = message
        self.level, self.html = self._get_level_and_html(level, html)
        self.timestamp = self._get_timestamp(timestamp)
        self.linkable = linkable

    @utils.setter
    def message(self, msg):
        if not isinstance(msg, basestring):
            msg = utils.unic(msg)
        return msg.replace('\r\n', '\n')

    def _get_level_and_html(self, level, html):
        level = level.upper()
        if level == 'HTML':
            return 'INFO', True
        if level not in LEVELS:
            raise DataError("Invalid log level '%s'" % level)
        return level, html

    def _get_timestamp(self, timestamp):
        if timestamp:
            return timestamp
        return utils.get_timestamp(daysep='', daytimesep=' ',
                                   timesep=':', millissep='.')

    def get_timestamp(self, sep=' '):
        return self.timestamp.replace(' ', sep)

    @property
    def time(self):
        if ' ' not in self.timestamp:
            return self.timestamp
        return self.timestamp.split()[1]


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

    def __init__(self, logger):
        self.logger = logger
        default = lambda *args: None
        for name in self._methods:
            try:
                method = getattr(logger, name)
            except AttributeError:
                method = getattr(logger, self._toCamelCase(name), default)
            setattr(self, name, method)

    def _toCamelCase(self, name):
        parts = name.split('_')
        return ''.join([parts[0]] + [part.capitalize() for part in parts[1:]])
