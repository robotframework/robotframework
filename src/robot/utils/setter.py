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

from typing import Any, Callable, Generic, overload, TypeVar


T = TypeVar('T')
V = TypeVar('V')


class setter(Generic[V]):

    def __init__(self, method: Callable[[T, Any], V]):
        self.method = method
        self.attr_name = '_setter__' + method.__name__
        self.__doc__ = method.__doc__

    @overload
    def __get__(self, instance: None, owner: 'type[T]') -> 'setter':
        ...

    @overload
    def __get__(self, instance: T, owner: 'type[T]') -> V:
        ...

    def __get__(self, instance: 'T|None', owner: 'type[T]') -> 'V|setter':
        if instance is None:
            return self
        try:
            return getattr(instance, self.attr_name)
        except AttributeError:
            raise AttributeError(self.method.__name__)

    def __set__(self, instance: T, value: Any):
        if instance is not None:
            setattr(instance, self.attr_name, self.method(instance, value))


class SetterAwareType(type):

    def __new__(cls, name, bases, dct):
        if '__slots__' in dct:
            slots = list(dct['__slots__'])
            for item in dct.values():
                if isinstance(item, setter):
                    slots.append(item.attr_name)
            dct['__slots__'] = slots
        return type.__new__(cls, name, bases, dct)
