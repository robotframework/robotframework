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


class setter(object):

    def __init__(self, method):
        self.method = method
        self.attr_name = '_setter__' + method.__name__
        self.__doc__ = method.__doc__

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return getattr(instance, self.attr_name)
        except AttributeError:
            raise AttributeError(self.method.__name__)

    def __set__(self, instance, value):
        if instance is None:
            return
        setattr(instance, self.attr_name, self.method(instance, value))


class SetterAwareType(type):

    def __new__(cls, name, bases, dct):
        slots = dct.get('__slots__')
        if slots is not None:
            for item in dct.values():
                if isinstance(item, setter):
                    slots.append(item.attr_name)
        return type.__new__(cls, name, bases, dct)
