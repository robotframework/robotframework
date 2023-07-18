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

from functools import total_ordering
from typing import (Any, Iterable, Iterator, MutableSequence, overload, TYPE_CHECKING,
                    Type, TypeVar)

from robot.utils import copy_signature, KnownAtRuntime, type_name

from .modelobject import DataDict

if TYPE_CHECKING:
    from .visitor import SuiteVisitor


T = TypeVar('T')
Self = TypeVar('Self', bound='ItemList')


@total_ordering
class ItemList(MutableSequence[T]):
    """List of items of a certain enforced type.

    New items can be created using the :meth:`create` method and existing items
    added using the common list methods like :meth:`append` or :meth:`insert`.
    In addition to the common type, items can have certain common and
    automatically assigned attributes.

    Starting from Robot Framework 6.1, items can be added as dictionaries and
    actual items are generated based on them automatically. If the type has
    a ``from_dict`` class method, it is used, and otherwise dictionary data is
    passed to the type as keyword arguments.
    """

    __slots__ = ['_item_class', '_common_attrs', '_items']
    # TypeVar T needs to be applied to a variable to be compatible with @copy_signature
    item_type: Type[T] = KnownAtRuntime

    def __init__(self, item_class: Type[T],
                 common_attrs: 'dict[str, Any]|None' = None,
                 items: 'Iterable[T|DataDict]' = ()):
        self._item_class = item_class
        self._common_attrs = common_attrs
        self._items: 'list[T]' = []
        if items:
            self.extend(items)

    @copy_signature(item_type)
    def create(self, *args, **kwargs) -> T:
        """Create a new item using the provided arguments."""
        return self.append(self._item_class(*args, **kwargs))

    def append(self, item: 'T|DataDict') -> T:
        item = self._check_type_and_set_attrs(item)
        self._items.append(item)
        return item

    def _check_type_and_set_attrs(self, item: 'T|DataDict') -> T:
        if not isinstance(item, self._item_class):
            if isinstance(item, dict):
                item = self._item_from_dict(item)
            else:
                raise TypeError(f'Only {type_name(self._item_class)} objects '
                                f'accepted, got {type_name(item)}.')
        if self._common_attrs:
            for attr, value in self._common_attrs.items():
                setattr(item, attr, value)
        return item

    def _item_from_dict(self, data: DataDict) -> T:
        if hasattr(self._item_class, 'from_dict'):
            return self._item_class.from_dict(data)    # type: ignore
        return self._item_class(**data)

    def extend(self, items: 'Iterable[T|DataDict]'):
        self._items.extend(self._check_type_and_set_attrs(i) for i in items)

    def insert(self, index: int, item: 'T|DataDict'):
        item = self._check_type_and_set_attrs(item)
        self._items.insert(index, item)

    def index(self, item: T, *start_and_end) -> int:
        return self._items.index(item, *start_and_end)

    def clear(self):
        self._items = []

    def visit(self, visitor: 'SuiteVisitor'):
        for item in self:
            item.visit(visitor)    # type: ignore

    def __iter__(self) -> Iterator[T]:
        index = 0
        while index < len(self._items):
            yield self._items[index]
            index += 1

    @overload
    def __getitem__(self, index: int) -> T:
        ...

    @overload
    def __getitem__(self: Self, index: slice) -> Self:
        ...

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self._create_new_from(self._items[index])
        return self._items[index]

    def _create_new_from(self: Self, items: Iterable[T]) -> Self:
        # Cannot pass common_attrs directly to new object because all
        # subclasses don't have compatible __init__.
        new = type(self)(self._item_class)
        new._common_attrs = self._common_attrs
        new.extend(items)
        return new

    @overload
    def __setitem__(self, index: int, item: 'T|DataDict'):
        ...

    @overload
    def __setitem__(self, index: slice, item: 'Iterable[T|DataDict]'):
        ...

    def __setitem__(self, index, item):
        if isinstance(index, slice):
            self._items[index] = [self._check_type_and_set_attrs(i) for i in item]
        else:
            self._items[index] = self._check_type_and_set_attrs(item)

    def __delitem__(self, index: 'int|slice'):
        del self._items[index]

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def __len__(self) -> int:
        return len(self._items)

    def __str__(self) -> str:
        return str(list(self))

    def __repr__(self) -> str:
        class_name = type(self).__name__
        item_name = self._item_class.__name__
        return f'{class_name}(item_class={item_name}, items={self._items})'

    def count(self, item: T) -> int:
        return self._items.count(item)

    def sort(self, **config):
        self._items.sort(**config)

    def reverse(self):
        self._items.reverse()

    def __reversed__(self) -> Iterator[T]:
        index = 0
        while index < len(self._items):
            yield self._items[len(self._items) - index - 1]
            index += 1

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, ItemList)
                and self._is_compatible(other)
                and self._items == other._items)

    def _is_compatible(self, other) -> bool:
        return (self._item_class is other._item_class
                and self._common_attrs == other._common_attrs)

    def __lt__(self, other: 'ItemList[T]') -> bool:
        if not isinstance(other, ItemList):
            raise TypeError(f'Cannot order ItemList and {type_name(other)}.')
        if not self._is_compatible(other):
            raise TypeError('Cannot order incompatible ItemLists.')
        return self._items < other._items

    def __add__(self: Self, other: 'ItemList[T]') -> Self:
        if not isinstance(other, ItemList):
            raise TypeError(f'Cannot add ItemList and {type_name(other)}.')
        if not self._is_compatible(other):
            raise TypeError('Cannot add incompatible ItemLists.')
        return self._create_new_from(self._items + other._items)

    def __iadd__(self: Self, other: Iterable[T]) -> Self:
        if isinstance(other, ItemList) and not self._is_compatible(other):
            raise TypeError('Cannot add incompatible ItemLists.')
        self.extend(other)
        return self

    def __mul__(self: Self, count: int) -> Self:
        return self._create_new_from(self._items * count)

    def __imul__(self: Self, count: int) -> Self:
        self._items *= count
        return self

    def __rmul__(self: Self, count: int) -> Self:
        return self * count

    def to_dicts(self) -> 'list[DataDict]':
        """Return list of items converted to dictionaries.

        Items are converted to dictionaries using the ``to_dict`` method, if
        they have it, or the built-in ``vars()``.

        New in Robot Framework 6.1.
        """
        if not hasattr(self._item_class, 'to_dict'):
            return [vars(item) for item in self]
        return [item.to_dict() for item in self]    # type: ignore
