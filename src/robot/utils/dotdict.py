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

from collections import OrderedDict

from .robottypes import is_dict_like


class DotDict(OrderedDict):

    def __init__(self, *args, **kwds):
        args = [self._convert_nested_initial_dicts(a) for a in args]
        kwds = self._convert_nested_initial_dicts(kwds)
        OrderedDict.__init__(self, *args, **kwds)

    def _convert_nested_initial_dicts(self, value):
        items = value.items() if is_dict_like(value) else value
        return OrderedDict((key, self._convert_nested_dicts(value))
                           for key, value in items)

    def _convert_nested_dicts(self, value):
        if isinstance(value, DotDict):
            return value
        if is_dict_like(value):
            return DotDict(value)
        if isinstance(value, list):
            value[:] = [self._convert_nested_dicts(item) for item in value]
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
