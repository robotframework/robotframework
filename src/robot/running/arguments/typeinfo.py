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

import sys
from collections.abc import Mapping, Sequence, Set
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, ForwardRef, get_args, get_origin, get_type_hints, Literal, Union

# Standard get_args and get_origin handle at least Annotated wrong in Python 3.8.
if sys.version_info < (3, 9):
    try:
        from typing_extensions import get_args, get_origin
    except ImportError:
        pass
# typing_extensions.Literal is typing.Literal with Python 3.10.1 and newer.
if sys.version_info < (3, 10, 1):
    try:
        from typing_extensions import Literal as ExtLiteral
    except ImportError:
        ExtLiteral = Literal
else:
    ExtLiteral = Literal
# NotRequired and Required are new in Python 3.11.
if sys.version_info >= (3, 11):
    from typing import NotRequired, Required
else:
    try:
        from typing_extensions import NotRequired, Required
    except ImportError:
        NotRequired = Required = object()

from robot.conf import Languages, LanguagesLike
from robot.errors import DataError
from robot.utils import (
    is_union, NOT_SET, plural_or_not as s, Secret, setter, SetterAwareType, type_name,
    type_repr, typeddict_types
)
from robot.variables import search_variable, VariableMatch

from ..context import EXECUTION_CONTEXTS
from .customconverters import CustomArgumentConverters
from .typeconverters import TypeConverter

TYPE_NAMES = {
    "...": Ellipsis,
    "ellipsis": Ellipsis,
    "any": Any,
    "object": object,
    "str": str,
    "string": str,
    "unicode": str,
    "bool": bool,
    "boolean": bool,
    "int": int,
    "integer": int,
    "long": int,
    "float": float,
    "double": float,
    "decimal": Decimal,
    "bytes": bytes,
    "bytearray": bytearray,
    "datetime": datetime,
    "date": date,
    "timedelta": timedelta,
    "path": Path,
    "none": type(None),
    "sequence": Sequence,
    "list": list,
    "tuple": tuple,
    "set": set,
    "frozenset": frozenset,
    "mapping": Mapping,
    "map": Mapping,
    "dictionary": dict,
    "dict": dict,
    "union": Union,
    "literal": Literal,
    "secret": Secret,
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
    __slots__ = ("name", "type")

    def __init__(
        self,
        name: "str|None" = None,
        type: Any = NOT_SET,
        nested: "Sequence[TypeInfo]|None" = None,
    ):
        if type is NOT_SET:
            type = TYPE_NAMES.get(name.lower()) if name else None
        self.name = name
        self.type = type
        self.nested = nested

    @setter
    def nested(self, nested: "Sequence[TypeInfo]") -> "tuple[TypeInfo, ...]|None":
        """Nested types as a tuple of ``TypeInfo`` objects.

        Used with parameterized types and unions.
        """
        typ = self.type
        if self.is_union:
            return self._validate_union(nested)
        if nested is None:
            return None
        if typ is None:
            return tuple(nested)
        if typ is Literal:
            return self._validate_literal(nested)
        if isinstance(typ, type):
            if issubclass(typ, tuple):
                if nested[-1].type is Ellipsis:
                    return self._validate_nested_count(
                        nested, 2, "Homogenous tuple", offset=-1
                    )
                return tuple(nested)
            if (
                issubclass(typ, Sequence)
                and not issubclass(typ, (str, bytes, bytearray, memoryview))
            ):  # fmt: skip
                return self._validate_nested_count(nested, 1)
            if issubclass(typ, Set):
                return self._validate_nested_count(nested, 1)
            if issubclass(typ, Mapping):
                return self._validate_nested_count(nested, 2)
        if typ in TYPE_NAMES.values():
            self._report_nested_error(nested)
        return tuple(nested)

    def _validate_union(self, nested):
        if not nested:
            raise DataError("Union cannot be empty.")
        return tuple(nested)

    def _validate_literal(self, nested):
        if not nested:
            raise DataError("Literal cannot be empty.")
        for info in nested:
            if not isinstance(info.type, LITERAL_TYPES):
                raise DataError(
                    f"Literal supports only integers, strings, bytes, Booleans, enums "
                    f"and None, value {info.name} is {type_name(info.type)}."
                )
        return tuple(nested)

    def _validate_nested_count(self, nested, expected, kind=None, offset=0):
        if len(nested) != expected:
            self._report_nested_error(nested, expected, kind, offset)
        return tuple(nested)

    def _report_nested_error(self, nested, expected=0, kind=None, offset=0):
        expected += offset
        actual = len(nested) + offset
        args = ", ".join(str(n) for n in nested)
        kind = kind or f"'{self.name}{'[]' if expected > 0 else ''}'"
        if expected == 0:
            raise DataError(
                f"{kind} does not accept parameters, "
                f"'{self.name}[{args}]' has {actual}."
            )
        raise DataError(
            f"{kind} requires exactly {expected} parameter{s(expected)}, "
            f"'{self.name}[{args}]' has {actual}."
        )

    @property
    def is_union(self):
        return self.name == "Union"

    @classmethod
    def from_type_hint(cls, hint: Any, sequence_is_union: bool = False) -> "TypeInfo":
        """Construct a ``TypeInfo`` based on a type hint.

        The type hint can be in various different formats:

        - an actual type such as ``int``
        - a parameterized type such as ``list[int]``
        - a union such as ``int | float``
        - a string such as ``'int'``, ``'list[int]'`` or ``'int | float'``
        - a ``TypedDict`` (represented as a :class:`TypedDictInfo`)
        - if ``sequence_is_union`` is ``True``, a sequence of type hints like
          ``[int, float]`` or ``('int', 'list[int]')`` creates a union

        In special cases using a more specialized method like :meth:`from_type`
        may be more appropriate than using this generic method.

        Prior to Robot Framework 7.4, sequences always created a union. If you
        need to handle sequences as unions, it is recommended to call
        :meth:`from_sequence` explicitly.
        """
        if hint is NOT_SET:
            return cls()
        if isinstance(hint, cls):
            return hint
        if isinstance(hint, ForwardRef):
            hint = hint.__forward_arg__
        if isinstance(hint, typeddict_types):
            return TypedDictInfo(hint.__name__, hint)
        if is_union(hint):
            nested = [cls.from_type_hint(a) for a in get_args(hint)]
            return cls("Union", nested=nested)
        origin = get_origin(hint)
        if origin:
            args = get_args(hint)
            if origin is Literal or origin is ExtLiteral:
                origin = Literal
                nested = [
                    cls(a.name if isinstance(a, Enum) else repr(a), a) for a in args
                ]
            elif args:
                nested = [cls.from_type_hint(a) for a in args]
            else:
                nested = None
            return cls(type_repr(hint, nested=False), origin, nested)
        if isinstance(hint, str):
            return cls.from_string(hint)
        if hint is Any:
            return cls("Any", hint)
        if hint is None:
            return cls("None", type(None))
        if hint is Ellipsis:
            return cls("...", hint)
        if hint is Union:  # Plain Union without params.
            return cls("Union")
        if isinstance(hint, type):
            return cls(type_repr(hint), hint)
        if isinstance(hint, Sequence):
            if sequence_is_union:
                return cls.from_sequence(hint)
            if isinstance(hint, list):
                # Better string representation with Callable params and other lists.
                items = [t.__name__ if isinstance(t, type) else repr(t) for t in hint]
                return cls(f"[{', '.join(items)}]")
        return cls(str(hint))

    @classmethod
    def from_type(cls, hint: type) -> "TypeInfo":
        """Construct a ``TypeInfo`` based on an actual type.

        Use :meth:`from_type_hint` if the type hint can also be something else
        than a concrete type such as a string or a type expression.
        """
        return cls(type_repr(hint), hint)

    @classmethod
    def from_string(cls, hint: str) -> "TypeInfo":
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
    def from_sequence(cls, sequence: Sequence) -> "TypeInfo":
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
            info = cls.from_type_hint(typ, sequence_is_union=True)
            if info.is_union:
                infos.extend(info.nested)
            else:
                infos.append(info)
        if len(infos) == 1:
            return infos[0]
        return cls("Union", nested=infos)

    @classmethod
    def from_variable(
        cls,
        variable: "str|VariableMatch",
        handle_list_and_dict: bool = True,
    ) -> "TypeInfo":
        """Construct a ``TypeInfo`` based on a variable.

        Type can be specified using syntax like ``${x: int}``.

        :param variable: Variable as a string or as an already parsed
            ``VariableMatch`` object.
        :param handle_list_and_dict: When ``True``, types in list and dictionary
            variables get ``list[]`` and ``dict[]`` decoration implicitly.
            For example, ``@{x: int}``, ``&{x: int}`` and ``&{x: str=int}``
            yield types ``list[int]``, ``dict[Any, int]`` and ``dict[str, int]``,
            respectively.
        :raises: ``DataError`` if variable has an unrecognized type. Variable
            not having a type is not an error.

        New in Robot Framework 7.3.
        """
        if isinstance(variable, str):
            variable = search_variable(variable, parse_type=True)
        if not variable.type:
            return cls()
        type_ = variable.type
        if handle_list_and_dict:
            if variable.identifier == "@":
                type_ = f"list[{type_}]"
            elif variable.identifier == "&":
                if "=" in type_:
                    kt, vt = type_.split("=", 1)
                else:
                    kt, vt = "Any", type_
                type_ = f"dict[{kt}, {vt}]"
        info = cls.from_string(type_)
        cls._validate_var_type(info)
        return info

    @classmethod
    def _validate_var_type(cls, info):
        if info.type is None:
            raise DataError(f"Unrecognized type '{info.name}'.")
        if info.nested and info.type is not Literal:
            for nested in info.nested:
                cls._validate_var_type(nested)

    def convert(
        self,
        value: Any,
        name: "str|None" = None,
        custom_converters: "CustomArgumentConverters|dict|None" = None,
        languages: "LanguagesLike" = None,
        kind: str = "Argument",
        allow_unknown: bool = False,
    ) -> object:
        """Convert ``value`` based on type information this ``TypeInfo`` contains.

        :param value: Value to convert.
        :param name: Name of the argument or other thing to convert.
            Used only for error reporting.
        :param custom_converters: Custom argument converters.
        :param languages: Language configuration. During execution, uses the
            current language configuration by default.
        :param kind: Type of the thing to be converted.
            Used only for error reporting.
        :param allow_unknown: If ``False``, a ``TypeError`` is raised if there
            is no converter for this type or to its nested types. If ``True``,
            conversion returns the original value instead.
        :raises: ``ValueError`` if conversion fails and ``TypeError`` if there is
            no converter for this type and unknown converters are not accepted.
        :return: Converted value.
        """
        converter = self.get_converter(custom_converters, languages, allow_unknown)
        return converter.convert(value, name, kind)

    def get_converter(
        self,
        custom_converters: "CustomArgumentConverters|dict|None" = None,
        languages: "LanguagesLike" = None,
        allow_unknown: bool = False,
    ) -> TypeConverter:
        """Get argument converter for this ``TypeInfo``.

        :param custom_converters: Custom argument converters.
        :param languages: Language configuration. During execution, uses the
            current language configuration by default.
        :param allow_unknown: If ``False``, a ``TypeError`` is raised if there
            is no converter for this type or to its nested types. If ``True``,
            a special ``UnknownConverter`` is returned instead.
        :raises: ``TypeError`` if there is no converter and unknown converters
            are not accepted.
        :return: ``TypeConverter``.

        The :meth:`convert` method handles the common conversion case, but this
        method can be used if the converter is needed multiple times or its
        needed also for other purposes than conversion.

        New in Robot Framework 7.2.
        """
        if isinstance(custom_converters, dict):
            custom_converters = CustomArgumentConverters.from_dict(custom_converters)
        if not languages and EXECUTION_CONTEXTS.current:
            languages = EXECUTION_CONTEXTS.current.languages
        elif not isinstance(languages, Languages):
            languages = Languages(languages)
        converter = TypeConverter.converter_for(self, custom_converters, languages)
        if not allow_unknown:
            converter.validate()
        return converter

    def __str__(self):
        if self.is_union:
            return " | ".join(str(n) for n in self.nested)
        name = self.name or ""
        if self.nested is None:
            return name
        nested = ", ".join(str(n) for n in self.nested)
        return f"{name}[{nested}]"

    def __bool__(self):
        return self.name is not None


class TypedDictInfo(TypeInfo):
    """Represents ``TypedDict`` used as an argument."""

    is_typed_dict = True
    __slots__ = ("annotations", "required")

    def __init__(self, name: str, type: type):
        super().__init__(name, type)
        type_hints = self._get_type_hints(type)
        # __required_keys__ is new in Python 3.9.
        self.required = getattr(type, "__required_keys__", frozenset())
        if sys.version_info < (3, 11):
            self._handle_typing_extensions_required_and_not_required(type_hints)
        self.annotations = {
            name: TypeInfo.from_type_hint(hint) for name, hint in type_hints.items()
        }

    def _get_type_hints(self, type) -> "dict[str, Any]":
        try:
            return get_type_hints(type)
        except Exception:
            return type.__annotations__

    def _handle_typing_extensions_required_and_not_required(self, type_hints):
        # NotRequired and Required are handled automatically by Python 3.11 and newer,
        # but with older they appear in type hints and need to be handled separately.
        required = set(self.required)
        for key, hint in type_hints.items():
            origin = get_origin(hint)
            if origin is Required:
                required.add(key)
                type_hints[key] = get_args(hint)[0]
            elif origin is NotRequired:
                required.discard(key)
                type_hints[key] = get_args(hint)[0]
        self.required = frozenset(required)
