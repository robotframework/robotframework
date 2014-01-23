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

from robot.errors import DataError


class BaseLibrary:

    def get_handler(self, name):
        try:
            return self.handlers[name]
        except KeyError:
            raise DataError("No keyword handler with name '%s' found"  % name)

    def has_handler(self, name):
        return name in self.handlers

    def __len__(self):
        return len(self.handlers)
