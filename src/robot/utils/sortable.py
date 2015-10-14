#  Copyright 2008-2015 Nokia Solutions and Networks
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


class Sortable(object):
    """Base class for sorting based self._sort_key"""

    _sort_key = NotImplemented

    def __eq__(self, other):
        if not isinstance(other, Sortable):
            return False
        return self._sort_key == other._sort_key

    def __lt__(self, other):
        self.__verify_type(other)
        return self._sort_key < other._sort_key

    def __le__(self, other):
        self.__verify_type(other)
        return self._sort_key <= other._sort_key

    def __gt__(self, other):
        self.__verify_type(other)
        return self._sort_key > other._sort_key

    def __ge__(self, other):
        self.__verify_type(other)
        return self._sort_key >= other._sort_key

    def __hash__(self):
        return hash(self._sort_key)

    def __verify_type(self, other):
        if not isinstance(other, Sortable):
            raise TypeError("Cannot compare %s and %s." % (type(self), type(other)))
