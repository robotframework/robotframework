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

from collections.abc import MutableSequence
from functools import total_ordering

from robot.utils import type_name


@total_ordering
class ItemList(MutableSequence):
    __slots__ = ['_item_class', '_common_attrs', '_items']

    def __init__(self, item_class, common_attrs=None, items=None):
        self._item_class = item_class
        self._common_attrs = common_attrs
        self._items = []
        if items:
            self.extend(items)

    def create(self, *args, **kwargs):
        return self.append(self._item_class(*args, **kwargs))

    def append(self, item):
        self._check_type_and_set_attrs(item)
        self._items.append(item)
        return item

    def _check_type_and_set_attrs(self, *items):
        common_attrs = self._common_attrs or {}
        for item in items:
            if not isinstance(item, self._item_class):
                raise TypeError(f'Only {type_name(self._item_class)} objects '
                                f'accepted, got {type_name(item)}.')
            for attr in common_attrs:
                setattr(item, attr, common_attrs[attr])
        return items

    def extend(self, items):
        self._items.extend(self._check_type_and_set_attrs(*items))

    def insert(self, index, item):
        self._check_type_and_set_attrs(item)
        self._items.insert(index, item)

    def index(self, item, *start_and_end):
        return self._items.index(item, *start_and_end)

    def clear(self):
        self._items = []

    def visit(self, visitor):
        for item in self:
            item.visit(visitor)

    def __iter__(self):
        index = 0
        while index < len(self._items):
            yield self._items[index]
            index += 1

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self._create_new_from(self._items[index])
        return self._items[index]

    def _create_new_from(self, items):
        # Cannot pass common_attrs directly to new object because all
        # subclasses don't have compatible __init__.
        new = type(self)(self._item_class)
        new._common_attrs = self._common_attrs
        new.extend(items)
        return new

    def __setitem__(self, index, item):
        if isinstance(index, slice):
            self._check_type_and_set_attrs(*item)
        else:
            self._check_type_and_set_attrs(item)
        self._items[index] = item

    def __delitem__(self, index):
        del self._items[index]

    def __contains__(self, item):
        return item in self._items

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        class_name = type(self).__name__
        item_name = self._item_class.__name__
        return f'{class_name}(item_class={item_name}, items={self._items})'

    def count(self, item):
        return self._items.count(item)

    def sort(self):
        self._items.sort()

    def reverse(self):
        self._items.reverse()

    def __reversed__(self):
        index = 0
        while index < len(self._items):
            yield self._items[len(self._items) - index - 1]
            index += 1

    def __eq__(self, other):
        return (isinstance(other, ItemList)
                and self._is_compatible(other)
                and self._items == other._items)

    def _is_compatible(self, other):
        return (self._item_class is other._item_class
                and self._common_attrs == other._common_attrs)

    def __lt__(self, other):
        if not isinstance(other, ItemList):
            raise TypeError(f'Cannot order ItemList and {type_name(other)}.')
        if not self._is_compatible(other):
            raise TypeError('Cannot order incompatible ItemLists.')
        return self._items < other._items

    def __add__(self, other):
        if not isinstance(other, ItemList):
            raise TypeError(f'Cannot add ItemList and {type_name(other)}.')
        if not self._is_compatible(other):
            raise TypeError('Cannot add incompatible ItemLists.')
        return self._create_new_from(self._items + other._items)

    def __iadd__(self, other):
        if isinstance(other, ItemList) and not self._is_compatible(other):
            raise TypeError('Cannot add incompatible ItemLists.')
        self.extend(other)
        return self

    def __mul__(self, other):
        return self._create_new_from(self._items * other)

    def __imul__(self, other):
        self._items *= other
        return self

    def __rmul__(self, other):
        return self * other
