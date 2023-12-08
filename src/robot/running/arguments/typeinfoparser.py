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

from ast import literal_eval
from enum import auto, Enum
from dataclasses import dataclass
from typing import Literal

from .typeinfo import LITERAL_TYPES, TypeInfo


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
        closing_quote = None
        char = self.source[self.current-1]
        if char in ('"', "'"):
            end_at = {None}
            closing_quote = char
        elif char == 'b' and self.peek() in ('"', "'"):
            end_at = {None}
            closing_quote = self.advance()
        while True:
            char = self.peek()
            if char in end_at:
                break
            self.current += 1
            if char == closing_quote:
                break
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

    def parse(self) -> TypeInfo:
        self.tokens = TypeInfoTokenizer(self.source).tokenize()
        info = self.type()
        if not self.at_end:
            self.error(f"Extra content after '{info}'.")
        return info

    def type(self) -> TypeInfo:
        if not self.check(TypeInfoTokenType.NAME):
            self.error('Type name missing.')
        info = TypeInfo(self.advance().value)
        if self.match(TypeInfoTokenType.LEFT_SQUARE):
            info.nested = self.params(literal=info.type is Literal)
        if self.match(TypeInfoTokenType.PIPE):
            nested = [info] + self.union()
            info = TypeInfo('Union', nested=nested)
        return info

    def params(self, literal: bool = False) -> 'list[TypeInfo]':
        params = []
        while not params or self.match(TypeInfoTokenType.COMMA):
            param = self.type()
            if literal:
                param = self._literal_param(param)
            params.append(param)
        if not self.match(TypeInfoTokenType.RIGHT_SQUARE):
            self.error("Closing ']' missing.")
        return params

    def _literal_param(self, param: TypeInfo) -> TypeInfo:
        try:
            try:
                value = literal_eval(param.name)
            except ValueError:
                if param.name.isidentifier():
                    return TypeInfo(param.name, None)
                raise
            if not isinstance(value, LITERAL_TYPES):
                raise ValueError
        except (ValueError, SyntaxError):
            token = self.tokens[self.current-1]
            self.error(f"Invalid literal value {param.name!r}.", token)
        else:
            return TypeInfo(repr(value), value)

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

    def error(self, message: str, token: 'TypeInfoToken|None' = None):
        if not token:
            token = self.peek()
        position = f'index {token.position}' if token else 'end'
        raise ValueError(f"Parsing type {self.source!r} failed: "
                         f"Error at {position}: {message}")
