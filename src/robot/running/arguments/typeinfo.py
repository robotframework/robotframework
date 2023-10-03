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
from collections.abc import Mapping, Sequence, Set
from datetime import date, datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union

from robot.conf import LanguagesLike
from robot.errors import DataError
from robot.utils import (has_args, is_union, NOT_SET, plural_or_not as s, setter,
                         SetterAwareType, type_repr, typeddict_types)

from .customconverters import CustomArgumentConverters
from .typeconverters import TypeConverter


TYPE_NAMES = {
    '...': Ellipsis,
    'ellipsis': Ellipsis,
    'any': Any,
    'str': str,
    'string': str,
    'unicode': str,
    'bool': bool,
    'boolean': bool,
    'int': int,
    'integer': int,
    'long': int,
    'float': float,
    'double': float,
    'decimal': Decimal,
    'bytes': bytes,
    'bytearray': bytearray,
    'datetime': datetime,
    'date': date,
    'timedelta': timedelta,
    'path': Path,
    'none': type(None),
    'list': list,
    'sequence': list,
    'tuple': tuple,
    'dictionary': dict,
    'dict': dict,
    'mapping': dict,
    'map': dict,
    'set': set,
    'frozenset': frozenset,
    'union': Union
}


class TypeInfo(metaclass=SetterAwareType):
    """Represents argument type.

    With unions and parametrized types, :attr:`nested` contains nested types.
    """
    is_typed_dict = False
    __slots__ = ('name', 'type')

    def __init__(self, name: 'str|None' = None,
                 type: 'type|None' = None,
                 nested: 'Sequence[TypeInfo]' = ()):
        if name and not type:
            type = TYPE_NAMES.get(name.lower())
        self.name = name
        self.type = type
        self.nested = nested

    @setter
    def nested(self, nested: 'Sequence[TypeInfo]') -> 'tuple[TypeInfo, ...]':
        if self.is_union:
            if not nested:
                raise DataError('Union used as a type hint cannot be empty.')
            return tuple(nested)
        typ = self.type
        if typ is None or not nested:
            return tuple(nested)
        if not isinstance(typ, type):
            self._report_nested_error(nested, 0)
        elif issubclass(typ, tuple):
            if nested[-1].type is Ellipsis and len(nested) != 2:
                self._report_nested_error(nested, 1, 'Homogenous tuple', -1)
        elif issubclass(typ, Sequence) and not issubclass(typ, (str, bytes, bytearray)):
            if len(nested) != 1:
                self._report_nested_error(nested, 1)
        elif issubclass(typ, Set):
            if len(nested) != 1:
                self._report_nested_error(nested, 1)
        elif issubclass(typ, Mapping):
            if len(nested) != 2:
                self._report_nested_error(nested, 2)
        elif typ in TYPE_NAMES.values():
            self._report_nested_error(nested, 0)
        return tuple(nested)

    def _report_nested_error(self, nested, expected, kind=None, offset=0):
        args = ', '.join(str(n) for n in nested)
        kind = kind or f"'{self.name}{'[]' if expected > 0 else ''}'"
        if expected == 0:
            raise DataError(f"{kind} does not accept arguments, "
                            f"'{self.name}[{args}]' has {len(nested) + offset}.")
        raise DataError(f"{kind} requires exactly {expected} argument{s(expected)}, "
                        f"'{self.name}[{args}]' has {len(nested) + offset}.")

    @property
    def is_union(self):
        return self.name == 'Union'

    @classmethod
    def from_type_hint(cls, hint: Any) -> 'TypeInfo':
        if hint is NOT_SET:
            return cls()
        if isinstance(hint, typeddict_types):
            return TypedDictInfo(hint.__name__, hint)
        if is_union(hint):
            nested = [cls.from_type_hint(typ) for typ in hint.__args__]
            return cls('Union', nested=nested)
        if hasattr(hint, '__origin__'):
            if has_args(hint):
                nested = [cls.from_type_hint(t) for t in hint.__args__]
            else:
                nested = []
            return cls(type_repr(hint, nested=False), hint.__origin__, nested)
        if isinstance(hint, type):
            return cls(type_repr(hint), hint)
        if hint is None:
            return cls('None', type(None))
        if isinstance(hint, str):
            return cls.from_string(hint)
        if isinstance(hint, dict):
            return cls.from_dict(hint)
        if isinstance(hint, (tuple, list)):
            return cls.from_sequence(hint)
        if hint is Union:
            return cls('Union')
        if hint is Any:
            return cls('Any', hint)
        if hint is Ellipsis:
            return cls('...', hint)
        return cls(str(hint))

    @classmethod
    def from_type(cls, hint: type) -> 'TypeInfo':
        return cls(type_repr(hint), hint)

    @classmethod
    def from_string(cls, hint: str) -> 'TypeInfo':
        try:
            return TypeInfoParser(hint).parse()
        except ValueError as err:
            raise DataError(str(err))

    @classmethod
    def from_dict(cls, data: dict) -> 'TypeInfo':
        if not data:
            return cls()
        nested = [cls.from_type_hint(n) for n in data['nested']]
        return cls(data['name'], nested=nested)

    @classmethod
    def from_sequence(cls, sequence: 'tuple|list') -> 'TypeInfo':
        infos = []
        for typ in sequence:
            info = cls.from_type_hint(typ)
            if info.is_union:
                infos.extend(info.nested)
            else:
                infos.append(info)
        if len(infos) == 1:
            return infos[0]
        return cls('Union', nested=infos)

    def convert(self, value: Any,
                name: 'str|None' = None,
                custom_converters: 'CustomArgumentConverters|dict|None' = None,
                languages: 'LanguagesLike' = None,
                kind: str = 'Argument'):
        if isinstance(custom_converters, dict):
            custom_converters = CustomArgumentConverters.from_dict(custom_converters)
        converter = TypeConverter.converter_for(self, custom_converters, languages)
        if not converter:
            raise TypeError(f"No converter found for '{self}'.")
        return converter.convert(value, name, kind)

    def __str__(self):
        if self.is_union:
            return ' | '.join(str(n) for n in self.nested)
        if self.nested:
            nested = ', '.join(str(n) for n in self.nested)
            return f'{self.name}[{nested}]'
        return self.name or ''

    def __bool__(self):
        return self.name is not None


class TypedDictInfo(TypeInfo):
    is_typed_dict = True
    __slots__ = ('annotations', 'required')

    def __init__(self, name: str, type: type):
        super().__init__(name, type)
        self.annotations = {n: TypeInfo.from_type_hint(t)
                            for n, t in type.__annotations__.items()}
        # __required_keys__ is new in Python 3.9.
        self.required = getattr(type, '__required_keys__', frozenset())


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
            info = TypeInfo('Union', nested=nested)
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
