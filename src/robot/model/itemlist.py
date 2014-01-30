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

    def _check_type_and_set_attrs(self, item):
        if not isinstance(item, self._item_class):
            raise TypeError("Only '%s' objects accepted, got '%s'."
                            % (self._item_class.__name__, type(item).__name__))
        if self._common_attrs:
            for attr in self._common_attrs:
                setattr(item, attr, self._common_attrs[attr])

    def extend(self, items):
        for item in items:
            self._check_type_and_set_attrs(item)
        self._items += tuple(items)

    if hasattr(tuple, 'index'):  # tuples got index method in Python 2.6
        def index(self, item):
            return self._items.index(item)
    else:
        def index(self, item):
            return list(self._items).index(item)

    def clear(self):
        self._items = ()

    def visit(self, visitor):
        for item in self:
            item.visit(visitor)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        if isinstance(index, slice):
            raise TypeError("'%s' objects do not support slicing."
                            % type(self).__name__)
        return self._items[index]

    def __setitem__(self, index, item):
        if isinstance(index, slice):
            raise TypeError("'%s' objects do not support slicing."
                            % type(self).__name__)
        self._check_type_and_set_attrs(item)
        items = list(self._items)
        items[index] = item
        self._items = tuple(items)

    def __len__(self):
        return len(self._items)

    def __unicode__(self):
        return u'[%s]' % ', '.join(unicode(item) for item in self)

    def __str__(self):
        return unicode(self).encode('ASCII', 'replace')
