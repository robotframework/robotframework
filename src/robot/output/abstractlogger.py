#  Copyright 2008 Nokia Siemens Networks Oyj
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

from levels import LEVELS, get_level


class AbstractLogger:
    
    def __init__(self, level): 
        self.set_level(level)
        
    def set_level(self, level_string):
        old = self._get_old_level()
        self.level = get_level(level_string)
        return old

    def _get_old_level(self):
        try:
            old_int = self.level
        except AttributeError:
            return None
        for level, int_value in LEVELS.items():
            if int_value == old_int:
                return level
    
    def write(self, msg='', level='INFO', html=False):
        if self._is_logged(level):
            self._write(Message(msg, level, html))
            
    def _is_logged(self, msg_level_str, threshold_level_str=None):
        msg_level = get_level(msg_level_str)
        if threshold_level_str is None:
            threshold_level = self.level
        else:
            threshold_level = get_level(threshold_level_str)
        return msg_level >= threshold_level
    
    def _write(self, message):
        raise NotImplementedError
    
    def trace(self, msg=''):
        self.write(msg, 'TRACE')

    def debug(self, msg=''):
        self.write(msg, 'DEBUG')

    def info(self, msg=''):
        self.write(msg, 'INFO')

    def warn(self, msg=''):
        self.write(msg, 'WARN')

    def fail(self, msg=''):
        self.write(msg, 'FAIL')

    def error(self, msg=''):
        self.write(msg, 'ERROR')


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

