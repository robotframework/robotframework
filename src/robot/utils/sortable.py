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

from operator import eq, lt, le, gt, ge

from .robottypes import type_name


class Sortable(object):
    """Base class for sorting based self._sort_key"""

    _sort_key = NotImplemented

    def __test(self, operator, other, require_sortable=True):
        if isinstance(other, Sortable):
            return operator(self._sort_key, other._sort_key)
        if not require_sortable:
            return False
        raise TypeError("Cannot sort '%s' and '%s'."
                        % (type_name(self), type_name(other)))

    def __eq__(self, other):
        return self.__test(eq, other, require_sortable=False)

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.__test(lt, other)

    def __le__(self, other):
        return self.__test(le, other)

    def __gt__(self, other):
        return self.__test(gt, other)

    def __ge__(self, other):
        return self.__test(ge, other)

    def __hash__(self):
        return hash(self._sort_key)
