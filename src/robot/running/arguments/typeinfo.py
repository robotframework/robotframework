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

from enum import auto, Enum
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Union

from robot.errors import DataError
from robot.utils import has_args, is_union, NOT_SET, type_repr


Type = Union[type, str, tuple, type(NOT_SET)]


class TypeInfo:
    """Represents argument type. Only used by Libdoc.

    With unions and parametrized types, :attr:`nested` contains nested types.
    """
    __slots__ = ('type', 'nested')

    def __init__(self, type: Type = NOT_SET, nested: 'Sequence[TypeInfo]' = ()):
        # TODO: Fix type hint of `type`.
        # TODO: Handle type aliases here.
        self.type = type if type != '...' else Ellipsis
        self.nested = tuple(nested)

    @property
    def name(self) -> str:
        if isinstance(self.type, str):
            return self.type
        return type_repr(self.type, nested=False)

    # TODO: Add `union=False` to `__init__` and remove this property.
    @property
    def is_union(self) -> bool:
        if isinstance(self.type, str):
            return self.type == 'Union'
        return is_union(self.type, allow_tuple=True)

    @classmethod
    def from_type_hint(cls, hint: Type) -> 'TypeInfo':
        if isinstance(hint, TypeInfo):
            return hint
        if hint is NOT_SET:
            return cls()
        if isinstance(hint, str):
            return cls.from_sting(hint)
        if isinstance(hint, dict):
            return cls.from_dict(hint)
        if isinstance(hint, (tuple, list)):
            if len(hint) == 1:
                return cls(hint[0])
            nested = tuple(cls.from_type_hint(t) for t in hint)
            return cls('Union', nested)
        return cls.from_type(hint)

    @classmethod
    def from_type(cls, hint: type):
        if has_args(hint):
            nested = tuple(cls.from_type_hint(t) for t in hint.__args__)
        else:
            nested = ()
        if hasattr(hint, '__origin__') and not is_union(hint):
            hint = hint.__origin__
        return cls(hint, nested)

    @classmethod
    def from_sting(cls, hint: str) -> 'TypeInfo':
        try:
            return TypeInfoParser(hint).parse()
        except ValueError as err:
            raise DataError(str(err))

    @classmethod
    def from_dict(cls, data: dict) -> 'TypeInfo':
        if not data:
            return cls()
        nested = [cls.from_dict(n) for n in data['nested']]
        return cls(data['name'], nested)

    def __str__(self):
        if self.is_union:
            return ' | '.join(str(n) for n in self.nested)
        if self.nested:
            nested = ', '.join(str(n) for n in self.nested)
            return f'{self.name}[{nested}]'
        return self.name

    def __bool__(self):
        return self.type is not NOT_SET


class TypeInfoTokenType(Enum):
    NAME = auto()
    LEFT_SQUARE = auto()
    RIGHT_SQUARE = auto()
    PIPE = auto()
    COMMA = auto()

    def __repr__(self):
        return str(self)


@dataclass
class TypeInfoToken:
    type: TypeInfoTokenType
    value: str
    position: int = -1


class TypeInfoTokenizer:
    markers = {
        '[': TypeInfoTokenType.LEFT_SQUARE,
        ']': TypeInfoTokenType.RIGHT_SQUARE,
        '|': TypeInfoTokenType.PIPE,
        ',': TypeInfoTokenType.COMMA,
    }

    def __init__(self, source: str):
        self.source = source
        self.tokens: 'list[TypeInfoToken]' = []
        self.start = 0
        self.current = 0

    @property
    def at_end(self) -> bool:
        return self.current >= len(self.source)

    def tokenize(self) -> 'list[TypeInfoToken]':
        while not self.at_end:
            self.start = self.current
            char = self.advance()
            if char in self.markers:
                self.add_token(self.markers[char])
            elif char.strip():
                self.name()
        return self.tokens

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def peek(self) -> 'str|None':
        try:
            return self.source[self.current]
        except IndexError:
            return None

    def name(self):
        end_at = set(self.markers) | {None}
        while self.peek() not in end_at:
            self.current += 1
        self.add_token(TypeInfoTokenType.NAME)

    def add_token(self, type: TypeInfoTokenType):
        value = self.source[self.start:self.current].strip()
        self.tokens.append(TypeInfoToken(type, value, self.start))


class TypeInfoParser:

    def __init__(self, source: str):
        self.source = source
        self.tokens: 'list[TypeInfoToken]' = []
        self.current = 0

    @property
    def at_end(self) -> bool:
        return self.peek() is None

    def parse(self) -> 'TypeInfo':
        self.tokens = TypeInfoTokenizer(self.source).tokenize()
        info = self.type()
        if not self.at_end:
            self.error(f"Extra content after '{info}'.")
        return info

    def type(self) -> 'TypeInfo':
        if not self.check(TypeInfoTokenType.NAME):
            self.error('Type name missing.')
        info = TypeInfo(self.advance().value)
        if self.match(TypeInfoTokenType.LEFT_SQUARE):
            info.nested = self.params()
        if self.match(TypeInfoTokenType.PIPE):
            nested = [info] + self.union()
            info = TypeInfo('Union', nested)
        return info

    def params(self) -> 'list[TypeInfo]':
        params = []
        while not params or self.match(TypeInfoTokenType.COMMA):
            params.append(self.type())
        if not self.match(TypeInfoTokenType.RIGHT_SQUARE):
            self.error("Closing ']' missing.")
        return params

    def union(self) -> 'list[TypeInfo]':
        types = []
        while not types or self.match(TypeInfoTokenType.PIPE):
            info = self.type()
            if info.is_union:
                types.extend(info.nested)
            else:
                types.append(info)
        return types

    def match(self, *types: TypeInfoTokenType) -> bool:
        for typ in types:
            if self.check(typ):
                self.advance()
                return True
        return False

    def check(self, expected: TypeInfoTokenType) -> bool:
        peeked = self.peek()
        return peeked and peeked.type == expected

    def advance(self) -> 'TypeInfoToken|None':
        token = self.peek()
        if token:
            self.current += 1
        return token

    def peek(self) -> 'TypeInfoToken|None':
        try:
            return self.tokens[self.current]
        except IndexError:
            return None

    def error(self, message: str):
        token = self.peek()
        position = f'index {token.position}' if token else 'end'
        raise ValueError(f"Parsing type {self.source!r} failed: "
                         f"Error at {position}: {message}")
