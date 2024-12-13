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

from typing import TYPE_CHECKING

from robot.errors import DataError

if TYPE_CHECKING:
    from .loggerhelper import Message


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


class LogLevel:

    def __init__(self, level):
        self.priority = self._get_priority(level)
        self.level = level.upper()

    def is_logged(self, msg: 'Message'):
        return LEVELS[msg.level] >= self.priority and msg.message is not None

    def set(self, level):
        old = self.level
        self.__init__(level)
        return old

    def _get_priority(self, level):
        try:
            return LEVELS[level.upper()]
        except KeyError:
            raise DataError(f"Invalid log level '{level}'.")
