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

try:
    from collections import OrderedDict
except ImportError:  # New in Python 2.7
    from .ordereddict import OrderedDict

from .robottypes import is_dict_like, is_list_like
from .platform import PY2, PYPY


class DotDict(OrderedDict):

    # With PyPy 2 __setitem__ isn't called with initial items and thus
    # __init__ needs to be overridden to handle initial nested dicts.

    if PYPY and PY2:

        def __init__(self, *args, **kwds):
            args = [self._convert_nested_initial_dicts(a) for a in args]
            kwds = self._convert_nested_initial_dicts(kwds)
            OrderedDict.__init__(self, *args, **kwds)

        def _convert_nested_initial_dicts(self, value):
            items = value.items() if is_dict_like(value) else value
            return OrderedDict((key, self._convert_nested_dicts(value))
                               for key, value in items)

    def __setitem__(self, key, value):
        value = self._convert_nested_dicts(value)
        OrderedDict.__setitem__(self, key, value)

    def _convert_nested_dicts(self, value):
        if is_dict_like(value):
            return DotDict(value)
        if is_list_like(value):
            return [self._convert_nested_dicts(item) for item in value]
        return value

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        if not key.startswith('_OrderedDict__'):
            self[key] = value
        else:
            OrderedDict.__setattr__(self, key, value)

    def __delattr__(self, key):
        try:
            self.pop(key)
        except KeyError:
            OrderedDict.__delattr__(self, key)

    def __eq__(self, other):
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return '{%s}' % ', '.join('%r: %r' % (key, self[key]) for key in self)

    # Must use original dict.__repr__ to allow customising PrettyPrinter.
    __repr__ = dict.__repr__
