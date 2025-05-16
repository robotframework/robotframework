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

from typing import Callable, Generic, overload, Type, TypeVar, Union

T = TypeVar("T")
V = TypeVar("V")
A = TypeVar("A")


class setter(Generic[T, V, A]):
    """Modify instance attributes only when they are set, not when they are get.

    Usage::

        @setter
        def source(self, source: str|Path) -> Path:
            return source if isinstance(source, Path) else Path(source)

    The setter method is called when the attribute is assigned like::

        instance.source = 'example.txt'

    and the returned value is stored in the instance in an attribute like
    ``_setter__source``. When the attribute is accessed, the stored value is
    returned.

    The above example is equivalent to using the standard ``property`` as
    follows. The main benefit of using ``setter`` is that it avoids a dummy
    getter method::

        @property
        def source(self) -> Path:
            return self._source

        @source.setter
        def source(self, source: src|Path):
            self._source = source if isinstance(source, Path) else Path(source)

    When using ``setter`` with ``__slots__``, the special ``_setter__xxx``
    attributes needs to be added to ``__slots__`` as well. The provided
    :class:`SetterAwareType` metaclass can take care of that automatically.
    """

    def __init__(self, method: Callable[[T, V], A]):
        self.method = method
        self.attr_name = "_setter__" + method.__name__
        self.__doc__ = method.__doc__

    @overload
    def __get__(self, instance: None, owner: Type[T]) -> "setter": ...

    @overload
    def __get__(self, instance: T, owner: Type[T]) -> A: ...

    def __get__(self, instance: Union[T, None], owner: Type[T]) -> Union[A, "setter"]:
        if instance is None:
            return self
        try:
            return getattr(instance, self.attr_name)
        except AttributeError:
            raise AttributeError(self.method.__name__)

    def __set__(self, instance: T, value: V):
        if instance is not None:
            setattr(instance, self.attr_name, self.method(instance, value))


class SetterAwareType(type):
    """Metaclass for adding attributes used by :class:`setter` to ``__slots__``."""

    def __new__(cls, name, bases, dct):
        if "__slots__" in dct:
            slots = list(dct["__slots__"])
            for item in dct.values():
                if isinstance(item, setter):
                    slots.append(item.attr_name)
            dct["__slots__"] = slots
        return type.__new__(cls, name, bases, dct)
