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

from robot.utils import py2to3, PY3


if PY3:
    unicode = str


@py2to3
class ItemList(object):
    __slots__ = ['_item_class', '_common_attrs', '_items']

    def __init__(self, item_class, common_attrs=None, items=None):
        self._item_class = item_class
        self._common_attrs = common_attrs
        self._items = ()
        if items:
            self.extend(items)

    def create(self, *args, **kwargs):
        return self.append(self._item_class(*args, **kwargs))

    def append(self, item):
        self._check_type_and_set_attrs(item)
        self._items += (item,)
        return item

    def _check_type_and_set_attrs(self, *items):
        common_attrs = self._common_attrs or {}
        for item in items:
            if not isinstance(item, self._item_class):
                raise TypeError("Only %s objects accepted, got %s."
                                % (self._item_class.__name__,
                                   item.__class__.__name__))
            for attr in common_attrs:
                setattr(item, attr, common_attrs[attr])
        return items

    def extend(self, items):
        self._items += self._check_type_and_set_attrs(*items)

    def insert(self, index, item):
        self._check_type_and_set_attrs(item)
        items = list(self._items)
        items.insert(index, item)
        self._items = tuple(items)

    def index(self, item, *start_and_end):
        return self._items.index(item, *start_and_end)

    def clear(self):
        self._items = ()

    def visit(self, visitor):
        for item in self:
            item.visit(visitor)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        if not isinstance(index, slice):
            return self._items[index]
        items = self.__class__(self._item_class)
        items._common_attrs = self._common_attrs
        items.extend(self._items[index])
        return items

    def __setitem__(self, index, item):
        if isinstance(index, slice):
            self._check_type_and_set_attrs(*item)
        else:
            self._check_type_and_set_attrs(item)
        items = list(self._items)
        items[index] = item
        self._items = tuple(items)

    def __len__(self):
        return len(self._items)

    def __unicode__(self):
        return u'[%s]' % ', '.join(unicode(item) for item in self)
