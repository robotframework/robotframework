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

from collections.abc import Mapping, Sequence, Set
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, ForwardRef, get_type_hints, Literal, Union

from robot.conf import Languages, LanguagesLike
from robot.errors import DataError
from robot.utils import (has_args, is_union, NOT_SET, plural_or_not as s, setter,
                         SetterAwareType, type_name, type_repr, typeddict_types)

from ..context import EXECUTION_CONTEXTS
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
    'union': Union,
    'literal': Literal
}
LITERAL_TYPES = (int, str, bytes, bool, Enum, type(None))


class TypeInfo(metaclass=SetterAwareType):
    """Represents an argument type.

    Normally created using the :meth:`from_type_hint` classmethod.
    With unions and parametrized types, :attr:`nested` contains nested types.

    Values can be converted according to this type info by using the
    :meth:`convert` method.

    Part of the public API starting from Robot Framework 7.0. In such usage
    should be imported via the :mod:`robot.api` package.
    """
    is_typed_dict = False
    __slots__ = ('name', 'type')

    def __init__(self, name: 'str|None' = None,
                 type: Any = NOT_SET,
                 nested: 'Sequence[TypeInfo]|None' = None):
        if type is NOT_SET:
            type = TYPE_NAMES.get(name.lower()) if name else None
        self.name = name
        self.type = type
        self.nested = nested

    @setter
    def nested(self, nested: 'Sequence[TypeInfo]') -> 'tuple[TypeInfo, ...]|None':
        """Nested types as a tuple of ``TypeInfo`` objects.

        Used with parameterized types and unions.
        """
        typ = self.type
        if self.is_union:
            self._validate_union(nested)
        elif nested is None:
            return None
        elif typ is None:
            return tuple(nested)
        elif typ is Literal:
            self._validate_literal(nested)
        elif not isinstance(typ, type):
            self._report_nested_error(nested)
        elif issubclass(typ, tuple):
            if nested[-1].type is Ellipsis:
                self._validate_nested_count(nested, 2, 'Homogenous tuple', offset=-1)
        elif issubclass(typ, Sequence) and not issubclass(typ, (str, bytes, bytearray)):
            self._validate_nested_count(nested, 1)
        elif issubclass(typ, Set):
            self._validate_nested_count(nested, 1)
        elif issubclass(typ, Mapping):
            self._validate_nested_count(nested, 2)
        elif typ in TYPE_NAMES.values():
            self._report_nested_error(nested)
        return tuple(nested)

    def _validate_union(self, nested):
        if not nested:
            raise DataError('Union cannot be empty.')

    def _validate_literal(self, nested):
        if not nested:
            raise DataError('Literal cannot be empty.')
        for info in nested:
            if not isinstance(info.type, LITERAL_TYPES):
                raise DataError(f'Literal supports only integers, strings, bytes, '
                                f'Booleans, enums and None, value {info.name} is '
                                f'{type_name(info.type)}.')

    def _validate_nested_count(self, nested, expected, kind=None, offset=0):
        if len(nested) != expected:
            self._report_nested_error(nested, expected, kind, offset)

    def _report_nested_error(self, nested, expected=0, kind=None, offset=0):
        expected += offset
        actual = len(nested) + offset
        args = ', '.join(str(n) for n in nested)
        kind = kind or f"'{self.name}{'[]' if expected > 0 else ''}'"
        if expected == 0:
            raise DataError(f"{kind} does not accept parameters, "
                            f"'{self.name}[{args}]' has {actual}.")
        raise DataError(f"{kind} requires exactly {expected} parameter{s(expected)}, "
                        f"'{self.name}[{args}]' has {actual}.")

    @property
    def is_union(self):
        return self.name == 'Union'

    @classmethod
    def from_type_hint(cls, hint: Any) -> 'TypeInfo':
        """Construct a ``TypeInfo`` based on a type hint.

        The type hint can be in various different formats:

        - an actual type such as ``int``
        - a parameterized type such as ``list[int]``
        - a union such as ``int | float``
        - a string such as ``'int'``, ``'list[int]'`` or ``'int | float'``
        - a ``TypedDict`` (represented as a :class:`TypedDictInfo`)
        - a sequence of supported type hints to create a union from such as
          ``[int, float]`` or ``('int', 'list[int]')``

        In special cases, for example with dictionaries or sequences, using the
        more specialized methods like :meth:`from_dict` or :meth:`from_sequence`
        may be more appropriate than using this generic method.
        """
        if hint is NOT_SET:
            return cls()
        if isinstance(hint, ForwardRef):
            hint = hint.__forward_arg__
        if isinstance(hint, typeddict_types):
            return TypedDictInfo(hint.__name__, hint)
        if is_union(hint):
            nested = [cls.from_type_hint(a) for a in hint.__args__]
            return cls('Union', nested=nested)
        if hasattr(hint, '__origin__'):
            if hint.__origin__ is Literal:
                nested = [cls(repr(a) if not isinstance(a, Enum) else a.name, a)
                          for a in hint.__args__]
            elif has_args(hint):
                nested = [cls.from_type_hint(a) for a in hint.__args__]
            else:
                nested = None
            return cls(type_repr(hint, nested=False), hint.__origin__, nested)
        if isinstance(hint, str):
            return cls.from_string(hint)
        if isinstance(hint, (tuple, list)):
            return cls.from_sequence(hint)
        if isinstance(hint, type):
            return cls(type_repr(hint), hint)
        if hint is None:
            return cls('None', type(None))
        if hint is Union:    # Plain `Union` without params.
            return cls('Union')
        if hint is Any:
            return cls('Any', hint)
        if hint is Ellipsis:
            return cls('...', hint)
        return cls(str(hint))

    @classmethod
    def from_type(cls, hint: type) -> 'TypeInfo':
        """Construct a ``TypeInfo`` based on an actual type.

        Use :meth:`from_type_hint` if the type hint can also be something else
        than a concrete type such as a string.
        """
        return cls(type_repr(hint), hint)

    @classmethod
    def from_string(cls, hint: str) -> 'TypeInfo':
        """Construct a ``TypeInfo`` based on a string.

        In addition to just types names or their aliases like ``int`` or ``integer``,
        supports also parameterized types like ``list[int]`` as well as unions like
        ``int | float``.

        Use :meth:`from_type_hint` if the type hint can also be something else
        than a string such as an actual type.
        """
        # Needs to be imported here due to cyclic dependency.
        from .typeinfoparser import TypeInfoParser
        try:
            return TypeInfoParser(hint).parse()
        except ValueError as err:
            raise DataError(str(err))

    @classmethod
    def from_sequence(cls, sequence: 'tuple|list') -> 'TypeInfo':
        """Construct a ``TypeInfo`` based on a sequence of types.

        Types can be actual types, strings, or anything else accepted by
        :meth:`from_type_hint`. If the sequence contains just one type,
        a ``TypeInfo`` created based on it is returned. If there are more
        types, the returned ``TypeInfo`` represents a union. Using an empty
        sequence is an error.

        Use :meth:`from_type_hint` if other types than sequences need to
        supported.
        """
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
        """Convert ``value`` based on type information this ``TypeInfo`` contains.

        :param value: Value to convert.
        :param name: Name of the argument or other thing to convert.
            Used only for error reporting.
        :param custom_converters: Custom argument converters.
        :param languages: Language configuration. During execution, uses the
            current language configuration by default.
        :param kind: Type of the thing to be converted.
            Used only for error reporting.
        :raises: ``TypeError`` if there is no converter for this type or
            ``ValueError`` is conversion fails.
        :return: Converted value.
        """
        if isinstance(custom_converters, dict):
            custom_converters = CustomArgumentConverters.from_dict(custom_converters)
        if not languages and EXECUTION_CONTEXTS.current:
            languages = EXECUTION_CONTEXTS.current.languages
        elif not isinstance(languages, Languages):
            languages = Languages(languages)
        converter = TypeConverter.converter_for(self, custom_converters, languages)
        if not converter:
            raise TypeError(f"No converter found for '{self}'.")
        return converter.convert(value, name, kind)

    def __str__(self):
        if self.is_union:
            return ' | '.join(str(n) for n in self.nested)
        name = self.name or ''
        if self.nested is None:
            return name
        nested = ', '.join(str(n) for n in self.nested)
        return f'{name}[{nested}]'

    def __bool__(self):
        return self.name is not None


class TypedDictInfo(TypeInfo):
    """Represents ``TypedDict`` used as an argument."""

    is_typed_dict = True
    __slots__ = ('annotations', 'required')

    def __init__(self, name: str, type: type):
        super().__init__(name, type)
        try:
            type_hints = get_type_hints(type)
        except Exception:
            type_hints = type.__annotations__
        self.annotations = {name: TypeInfo.from_type_hint(hint)
                            for name, hint in type_hints.items()}
        # __required_keys__ is new in Python 3.9.
        self.required = getattr(type, '__required_keys__', frozenset())
