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

from typing import Union

from robot.utils import has_args, is_union, NOT_SET, type_repr


Type = Union[type, str, tuple, type(NOT_SET)]


class TypeInfo:
    """Represents argument type. Only used by Libdoc.

    With unions and parametrized types, :attr:`nested` contains nested types.
    """

    def __init__(self, type: Type = NOT_SET, nested: 'tuple[TypeInfo]' = ()):
        self.type = type
        self.nested = nested

    @property
    def name(self) -> str:
        if isinstance(self.type, str):
            return self.type
        return type_repr(self.type, nested=False)

    @property
    def is_union(self) -> bool:
        if isinstance(self.type, str):
            return self.type == 'Union'
        return is_union(self.type, allow_tuple=True)

    @classmethod
    def from_type(cls, type: Type) -> 'TypeInfo':
        if type is NOT_SET:
            return cls()
        if isinstance(type, dict):
            return cls.from_dict(type)
        if isinstance(type, (tuple, list)):
            if not type:
                return cls()
            if len(type) == 1:
                return cls(type[0])
            nested = tuple(cls.from_type(t) for t in type)
            return cls('Union', nested)
        if has_args(type):
            nested = tuple(cls.from_type(t) for t in type.__args__)
            return cls(type, nested)
        return cls(type)

    @classmethod
    def from_dict(cls, data: dict) -> 'TypeInfo':
        if not data:
            return cls()
        nested = tuple(cls.from_dict(n) for n in data['nested'])
        return cls(data['name'], nested)

    def __str__(self):
        if self.is_union:
            return ' | '.join(str(n) for n in self.nested)
        if isinstance(self.type, str):
            if self.nested:
                nested = ', '.join(str(n) for n in self.nested)
                return f'{self.name}[{nested}]'
            return self.name
        return type_repr(self.type)

    def __bool__(self):
        return self.type is not NOT_SET
