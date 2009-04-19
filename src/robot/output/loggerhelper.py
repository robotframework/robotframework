#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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
  "NONE"  : 100, 
  "ERROR" : 60,
  "FAIL"  : 50,
  "WARN"  : 40,
  "INFO"  : 30,
  "DEBUG" : 20,
  "TRACE" : 10,
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


class Message:
    
    def __init__(self, message, level, html=False):
        self.timestamp = utils.get_timestamp(daysep='', daytimesep=' ',
                                             timesep=':', millissep='.')
        self.level = level.upper()
        self.message = self._process_message(message)
        self.html = html
        
    def _process_message(self, msg):
        """Makes sure we have a string and no extra CR is written to log"""
        if not utils.is_str(msg):
            msg = utils.unic(msg)
        return msg.replace('\r\n', '\n')


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

