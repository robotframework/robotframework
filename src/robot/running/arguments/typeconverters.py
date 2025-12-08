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
from collections import OrderedDict
from collections.abc import Collection, Mapping, Sequence, Set
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from enum import Enum
from numbers import Integral, Real
from os import PathLike
from pathlib import Path, PurePath
from typing import Any, Literal, TYPE_CHECKING, Union

from robot.conf import Languages
from robot.libraries.DateTime import convert_date, convert_time
from robot.utils import (
    eq, get_error_message, plural_or_not as s, safe_str, Secret, seq2str, type_name
)

if TYPE_CHECKING:
    from .customconverters import ConverterInfo, CustomArgumentConverters
    from .typeinfo import TypedDictInfo, TypeInfo


NoneType = type(None)


class TypeConverter:
    type = None
    type_name = None  # Used also by Libdoc. Can be overridden by instances.
    abc = None
    value_types = (str,)
    doc = None
    nested: "list[TypeConverter]|dict[str, TypeConverter]|None"
    _converters = OrderedDict()

    def __init__(
        self,
        type_info: "TypeInfo",
        custom_converters: "CustomArgumentConverters|None" = None,
        languages: "Languages|None" = None,
    ):
        self.type_info = type_info
        self.custom_converters = custom_converters
        self.languages = languages
        self.nested = self._get_nested(type_info, custom_converters, languages)
        self.type_name = self._get_type_name()

    def _get_nested(
        self,
        type_info: "TypeInfo",
        custom_converters: "CustomArgumentConverters|None",
        languages: "Languages|None",
    ) -> "list[TypeConverter]|None":
        if not type_info.nested:
            return None
        return [
            self.converter_for(info, custom_converters, languages)
            for info in type_info.nested
        ]

    def _get_type_name(self) -> str:
        if self.type_name and not self.nested:
            return self.type_name
        return str(self.type_info)

    @property
    def languages(self) -> Languages:
        # Initialize only when needed to save time especially with Libdoc.
        if self._languages is None:
            self._languages = Languages()
        return self._languages

    @languages.setter
    def languages(self, languages: "Languages|None"):
        self._languages = languages

    @classmethod
    def register(cls, converter: "type[TypeConverter]") -> "type[TypeConverter]":
        cls._converters[converter.type] = converter
        return converter

    @classmethod
    def converter_for(
        cls,
        type_info: "TypeInfo",
        custom_converters: "CustomArgumentConverters|None" = None,
        languages: "Languages|None" = None,
    ) -> "TypeConverter":
        if type_info.type is None:
            return UnknownConverter(type_info)
        if custom_converters:
            info = custom_converters.get_converter_info(type_info.type)
            if info:
                return CustomConverter(type_info, info, languages)
        if type_info.type in cls._converters:
            conv_class = cls._converters[type_info.type]
            return conv_class(type_info, custom_converters, languages)
        for converter in cls._converters.values():
            if converter.handles(type_info):
                return converter(type_info, custom_converters, languages)
        return UnknownConverter(type_info)

    @classmethod
    def handles(cls, type_info: "TypeInfo") -> bool:
        handled = (cls.type, cls.abc) if cls.abc else cls.type
        return isinstance(type_info.type, type) and issubclass(type_info.type, handled)

    def convert(
        self,
        value: Any,
        name: "str|None" = None,
        kind: str = "Argument",
    ) -> Any:
        if self.no_conversion_needed(value):
            return value
        if not self._handles_value(value):
            return self._handle_error(value, name, kind)
        try:
            if not isinstance(value, str):
                return self._non_string_convert(value)
            return self._string_convert(value)
        except ValueError as error:
            return self._handle_error(value, name, kind, error)

    def no_conversion_needed(self, value: Any) -> bool:
        try:
            return isinstance(value, self.type_info.type)
        except TypeError:
            # Used type wasn't a class. Compare to generic type instead.
            if self.type and self.type is not self.type_info.type:
                return isinstance(value, self.type)
            return False

    def validate(self):
        """Validate converter. Raise ``TypeError`` for unrecognized types."""
        if self.nested:
            self._validate(self.nested)

    def _validate(self, nested):
        for converter in nested:
            converter.validate()

    def _handles_value(self, value):
        return isinstance(value, self.value_types)

    def _non_string_convert(self, value):
        return self._convert(value)

    def _string_convert(self, value):
        return self._convert(value)

    def _convert(self, value):
        raise NotImplementedError

    def _handle_error(self, value, name, kind, error=None):
        typ = "" if isinstance(value, str) else f" ({type_name(value)})"
        value = safe_str(value)
        kind = kind.capitalize() if kind.islower() else kind
        ending = f": {error}" if (error and error.args) else "."
        cannot_be_converted = f"cannot be converted to {self.type_name}{ending}"
        if name is None:
            raise ValueError(f"{kind} '{value}'{typ} {cannot_be_converted}")
        raise ValueError(
            f"{kind} '{name}' got value '{value}'{typ} that {cannot_be_converted}"
        )

    def _literal_eval(self, value, expected, name=None):
        try:
            value = literal_eval(value)
        except (ValueError, SyntaxError):
            # Original errors aren't too informative in these cases.
            raise ValueError("Invalid expression.")
        except TypeError as err:
            raise ValueError(f"Evaluating expression failed: {err}")
        if not isinstance(value, expected):
            raise ValueError(
                f"Value is {type_name(value)}, not {name or expected.__name__}."
            )
        return value

    def _remove_number_separators(self, value):
        if isinstance(value, str):
            for sep in " ", "_":
                if sep in value:
                    value = value.replace(sep, "")
        return value


@TypeConverter.register
class EnumConverter(TypeConverter):
    type = Enum

    @property
    def value_types(self):
        return (str, int) if issubclass(self.type_info.type, int) else (str,)

    def _non_string_convert(self, value):
        return self._find_by_int_value(self.type_info.type, value)

    def _string_convert(self, value):
        enum = self.type_info.type
        try:
            return enum[value]
        except KeyError:
            return self._find_by_normalized_name_or_int_value(enum, value)

    def _find_by_normalized_name_or_int_value(self, enum, value):
        members = sorted(enum.__members__)
        matches = [m for m in members if eq(m, value, ignore="_-")]
        if len(matches) == 1:
            return getattr(enum, matches[0])
        if len(matches) > 1:
            raise ValueError(
                f"{self.type_name} has multiple members matching '{value}'. "
                f"Available: {seq2str(matches)}"
            )
        try:
            if issubclass(self.type_info.type, int):
                return self._find_by_int_value(enum, value)
        except ValueError:
            members = [f"{m} ({getattr(enum, m)})" for m in members]
        raise ValueError(
            f"{self.type_name} does not have member '{value}'. "
            f"Available: {seq2str(members)}"
        )

    def _find_by_int_value(self, enum, value):
        value = int(value)
        for member in enum:
            if member.value == value:
                return member
        values = sorted(member.value for member in enum)
        raise ValueError(
            f"{self.type_name} does not have value '{value}'. "
            f"Available: {seq2str(values)}"
        )


@TypeConverter.register
class AnyConverter(TypeConverter):
    type = Any
    type_name = "Any"
    value_types = (Any,)

    @classmethod
    def handles(cls, type_info: "TypeInfo"):
        return type_info.type is cls.type

    def no_conversion_needed(self, value):
        return True

    def _convert(self, value):
        return value

    def _handles_value(self, value):
        return True


@TypeConverter.register
class ObjectConverter(AnyConverter):
    type = object
    type_name = "object"
    value_types = (Any,)


@TypeConverter.register
class StringConverter(TypeConverter):
    type = str
    type_name = "string"
    value_types = (Any,)

    def _handles_value(self, value):
        return True

    def _non_string_convert(self, value):
        if isinstance(value, Secret):
            raise ValueError
        if isinstance(value, (bytes, bytearray)):
            return value.decode("latin-1")
        try:
            return str(value)
        except Exception:
            raise ValueError(get_error_message())


@TypeConverter.register
class BooleanConverter(TypeConverter):
    type = bool
    type_name = "boolean"
    value_types = (str, int, float, NoneType)

    def _non_string_convert(self, value):
        return value

    def _string_convert(self, value):
        normalized = value.title()
        if normalized == "None":
            return None
        if normalized in self.languages.true_strings:
            return True
        if normalized in self.languages.false_strings:
            return False
        return value


@TypeConverter.register
class IntegerConverter(TypeConverter):
    type = int
    abc = Integral
    type_name = "integer"
    value_types = (str, float)

    def _non_string_convert(self, value):
        if value.is_integer():
            return int(value)
        raise ValueError("Conversion would lose precision.")

    def _string_convert(self, value):
        value = self._remove_number_separators(value)
        value, base = self._get_base(value)
        try:
            return int(value, base)
        except ValueError:
            if base == 10:
                try:
                    value, denominator = Decimal(value).as_integer_ratio()
                except (InvalidOperation, ValueError, OverflowError):
                    pass
                else:
                    if denominator != 1:
                        raise ValueError("Conversion would lose precision.")
                    return value
            raise ValueError

    def _get_base(self, value):
        value = value.lower()
        for prefix, base in [("0x", 16), ("0o", 8), ("0b", 2)]:
            if prefix in value:
                parts = value.split(prefix)
                if len(parts) == 2 and parts[0] in ("", "-", "+"):
                    return "".join(parts), base
        return value, 10


@TypeConverter.register
class FloatConverter(TypeConverter):
    type = float
    abc = Real
    type_name = "float"
    value_types = (str, Real)

    def _convert(self, value):
        try:
            return float(self._remove_number_separators(value))
        except ValueError:
            raise ValueError


@TypeConverter.register
class DecimalConverter(TypeConverter):
    type = Decimal
    type_name = "decimal"
    value_types = (str, int, float)

    def _convert(self, value):
        try:
            return Decimal(self._remove_number_separators(value))
        except InvalidOperation:
            # With Python 3 error messages by decimal module are not very
            # useful and cannot be included in our error messages:
            # https://bugs.python.org/issue26208
            raise ValueError


@TypeConverter.register
class BytesConverter(TypeConverter):
    type = bytes
    type_name = "bytes"
    value_types = (str, bytearray, Sequence, int)

    def _non_string_convert(self, value: "bytearray | Sequence | int") -> bytes:
        if isinstance(value, bytearray):
            return bytes(value)
        if isinstance(value, int):
            value = [value]
        return bytes([self._validate_int(v) for v in value])

    def _validate_int(self, value: object) -> int:
        try:
            value = int(value)  # type: ignore
        except Exception:
            raise ValueError(f"{value!r} is not an integer.")
        if value < 0 or value > 255:
            raise ValueError(f"{value} is not in range 0-255.")
        return value

    def _string_convert(self, value: str) -> bytes:
        try:
            return value.encode("latin-1")
        except UnicodeEncodeError as err:
            invalid = value[err.start : err.start + 1]
            raise ValueError(f"Character '{invalid}' cannot be mapped to a byte.")


@TypeConverter.register
class ByteArrayConverter(BytesConverter):
    type = bytearray
    type_name = "bytearray"
    value_types = (str, bytes, Sequence, int)

    def _non_string_convert(self, value: "bytes | Sequence | int") -> bytearray:
        if not isinstance(value, bytes):
            value = super()._non_string_convert(value)
        return bytearray(value)

    def _string_convert(self, value: str) -> bytearray:
        return bytearray(super()._string_convert(value))


@TypeConverter.register
class DateTimeConverter(TypeConverter):
    type = datetime
    type_name = "datetime"
    value_types = (str, int, float)

    def _convert(self, value):
        if isinstance(value, str) and value.lower() in ("now", "today"):
            return datetime.now()
        return convert_date(value, result_format="datetime")


@TypeConverter.register
class DateConverter(TypeConverter):
    type = date
    type_name = "date"

    def _convert(self, value):
        if isinstance(value, str) and value.lower() in ("now", "today"):
            return date.today()
        dt = convert_date(value, result_format="datetime")
        if dt.hour or dt.minute or dt.second or dt.microsecond:
            raise ValueError("Value is datetime, not date.")
        return dt.date()


@TypeConverter.register
class TimeDeltaConverter(TypeConverter):
    type = timedelta
    type_name = "timedelta"
    value_types = (str, int, float)

    def _convert(self, value):
        return convert_time(value, result_format="timedelta")


@TypeConverter.register
class PathConverter(TypeConverter):
    type = Path
    abc = PathLike
    type_name = "Path"
    value_types = (str, PurePath)

    def _convert(self, value):
        return Path(value)


@TypeConverter.register
class NoneConverter(TypeConverter):
    type = NoneType
    type_name = "None"

    @classmethod
    def handles(cls, type_info: "TypeInfo") -> bool:
        return type_info.type in (NoneType, None)

    def _string_convert(self, value):
        if value.upper() in ("NONE", ""):
            return None
        raise ValueError


@TypeConverter.register
class SequenceConverter(TypeConverter):
    type = Sequence
    type_name = "Sequence"
    value_types = (str, Sequence)

    def no_conversion_needed(self, value):
        if (
            isinstance(value, str)
            or not super().no_conversion_needed(value)
            or self._must_make_mutable(value)
        ):
            return False
        if not self.nested:
            return True
        no_conversion_needed = self.nested[0].no_conversion_needed
        return all(no_conversion_needed(v) for v in value)

    def _must_make_mutable(self, value):
        return not isinstance(value, self.type_info.type)

    def _string_convert(self, value):
        return self._convert(self._literal_eval(value, Sequence))

    def _convert(self, value):
        if self._must_make_mutable(value):
            value = list(value)
        if self.nested:
            value = self._convert_nested(value)
        return value

    def _convert_nested(self, value):
        result_type = type(value)
        convert = self.nested[0].convert
        value = [convert(v, name=str(i), kind="Item") for i, v in enumerate(value)]
        try:
            return result_type(value)
        except Exception:
            raise ValueError("Cannot recreate object after converting items.")


@TypeConverter.register
class ListConverter(SequenceConverter):
    type = list
    type_name = "list"

    def _must_make_immutable(self):
        return False

    def _string_convert(self, value):
        value = self._literal_eval(value, Sequence, name="list")
        return self._convert(list(value))

    def _non_string_convert(self, value):
        return self._convert(list(value))


@TypeConverter.register
class TupleConverter(TypeConverter):
    type = tuple
    type_name = "tuple"
    value_types = (str, Sequence)

    @property
    def homogenous(self) -> bool:
        nested = self.type_info.nested
        return nested and nested[-1].type is Ellipsis

    def no_conversion_needed(self, value):
        if isinstance(value, str) or not super().no_conversion_needed(value):
            return False
        if not self.nested:
            return True
        if self.homogenous:
            converter = self.nested[0]
            return all(converter.no_conversion_needed(v) for v in value)
        if len(value) != len(self.nested):
            return False
        return all(c.no_conversion_needed(v) for c, v in zip(self.nested, value))

    def _string_convert(self, value):
        value = self._literal_eval(value, Sequence, name="tuple")
        return self._convert_nested(tuple(value))

    def _non_string_convert(self, value):
        return self._convert_nested(tuple(value))

    def _convert_nested(self, value):
        if not self.nested:
            return value
        if self.homogenous:
            convert = self.nested[0].convert
            return tuple(
                convert(v, name=str(i), kind="Item") for i, v in enumerate(value)
            )
        if len(value) != len(self.nested):
            raise ValueError(
                f"Expected {len(self.nested)} item{s(self.nested)}, got {len(value)}."
            )
        return tuple(
            c.convert(v, name=str(i), kind="Item")
            for i, (c, v) in enumerate(zip(self.nested, value))
        )

    def _validate(self, nested: "list[TypeConverter]"):
        if self.homogenous:
            nested = nested[:-1]
        super()._validate(nested)


@TypeConverter.register
class TypedDictConverter(TypeConverter):
    type = "TypedDict"
    value_types = (str, Mapping)
    type_info: "TypedDictInfo"
    nested: "dict[str, TypeConverter]"

    def _get_nested(
        self,
        type_info: "TypedDictInfo",
        custom_converters: "CustomArgumentConverters|None",
        languages: "Languages|None",
    ) -> "dict[str, TypeConverter]":
        return {
            name: self.converter_for(info, custom_converters, languages)
            for name, info in type_info.annotations.items()
        }

    @classmethod
    def handles(cls, type_info: "TypeInfo") -> bool:
        return type_info.is_typed_dict

    def no_conversion_needed(self, value):
        if not isinstance(value, Mapping):
            return False
        for key in value:
            try:
                converter = self.nested[key]
            except KeyError:
                return False
            else:
                if not converter.no_conversion_needed(value[key]):
                    return False
        return set(value).issuperset(self.type_info.required)

    def _non_string_convert(self, value):
        return self._convert_items(value)

    def _string_convert(self, value):
        return self._convert_items(self._literal_eval(value, dict))

    def _convert_items(self, value):
        not_allowed = []
        for key in value:
            try:
                converter = self.nested[key]
            except KeyError:
                not_allowed.append(key)
            else:
                if converter:
                    value[key] = converter.convert(value[key], name=key, kind="Item")
        if not_allowed:
            error = f"Item{s(not_allowed)} {seq2str(sorted(not_allowed))} not allowed."
            available = [key for key in self.nested if key not in value]
            if available:
                error += f" Available item{s(available)}: {seq2str(sorted(available))}"
            raise ValueError(error)
        missing = [key for key in self.type_info.required if key not in value]
        if missing:
            raise ValueError(
                f"Required item{s(missing)} {seq2str(sorted(missing))} missing."
            )
        return value

    def _validate(self, nested: "dict[str, TypeConverter]"):
        super()._validate(nested.values())


@TypeConverter.register
class MappingConverter(TypeConverter):
    type = Mapping
    type_name = "Mapping"
    value_types = (str, Mapping)

    def no_conversion_needed(self, value):
        if (
            isinstance(value, str)
            or not super().no_conversion_needed(value)
            or self._must_make_mutable(value)
        ):
            return False
        if not self.nested:
            return True
        no_key_conversion = self.nested[0].no_conversion_needed
        no_value_conversion = self.nested[1].no_conversion_needed
        return all(
            no_key_conversion(k) and no_value_conversion(value[k]) for k in value
        )

    def _must_make_mutable(self, value):
        return not isinstance(value, self.type_info.type)

    def _string_convert(self, value):
        return self._convert(self._literal_eval(value, Mapping))

    def _convert(self, value):
        if self._must_make_mutable(value):
            value = dict(value)
        if self.nested:
            value = self._convert_nested(value)
        return value

    def _convert_nested(self, value):
        result_type = type(value)
        convert_key = self._get_converter(self.nested[0], "Key")
        convert_value = self._get_converter(self.nested[1], "Item")
        value = {convert_key(None, k): convert_value(k, value[k]) for k in value}
        try:
            return result_type(value)
        except Exception:
            raise ValueError("Cannot recreate object after converting items.")

    def _get_converter(self, converter, kind):
        return lambda name, value: converter.convert(value, name, kind=kind)


@TypeConverter.register
class DictionaryConverter(MappingConverter):
    type = dict
    type_name = "dictionary"

    def _must_make_immutable(self):
        return False

    def _string_convert(self, value):
        return self._convert(self._literal_eval(value, dict))

    def _non_string_convert(self, value):
        return self._convert(dict(value))


@TypeConverter.register
class SetConverter(TypeConverter):
    type = set
    abc = Set
    type_name = "set"
    value_types = (str, Collection)

    def no_conversion_needed(self, value):
        if isinstance(value, str) or not super().no_conversion_needed(value):
            return False
        if not self.nested:
            return True
        no_conversion_needed = self.nested[0].no_conversion_needed
        return all(no_conversion_needed(v) for v in value)

    def _string_convert(self, value):
        if value == "set()":  # literal_eval doesn't support "set()" with Python 3.8.
            return set()
        value = self._literal_eval(value, (set, Sequence), name="set")
        return self._convert_nested(set(value))

    def _non_string_convert(self, value):
        return self._convert_nested(set(value))

    def _convert_nested(self, value):
        if self.nested:
            convert = self.nested[0].convert
            value = {convert(v, kind="Item") for v in value}
        return value


@TypeConverter.register
class FrozenSetConverter(SetConverter):
    type = frozenset
    type_name = "frozenset"

    def _string_convert(self, value):
        if value == "frozenset()":  # literal_eval doesn't support "frozenset()".
            return frozenset()
        return frozenset(super()._string_convert(value))

    def _non_string_convert(self, value):
        return frozenset(super()._non_string_convert(value))


@TypeConverter.register
class UnionConverter(TypeConverter):
    type = Union

    def _get_type_name(self) -> str:
        names = [converter.type_name for converter in self.nested]
        return seq2str(names, quote="", lastsep=" or ")

    @classmethod
    def handles(cls, type_info: "TypeInfo") -> bool:
        return type_info.is_union

    def _handles_value(self, value):
        return True

    def no_conversion_needed(self, value):
        for converter in self.nested:
            if (
                converter.no_conversion_needed(value)
                and not isinstance(converter, ObjectConverter)
            ):  # fmt:skip
                return True
        return False

    def _convert(self, value):
        unknown_types = False
        for converter in self.nested:
            if converter:
                try:
                    return converter.convert(value)
                except ValueError:
                    pass
            else:
                unknown_types = True
        if unknown_types:
            return value
        raise ValueError


@TypeConverter.register
class LiteralConverter(TypeConverter):
    type = Literal
    type_name = "Literal"
    value_types = (Any,)

    def _get_type_name(self) -> str:
        names = [info.name for info in self.type_info.nested]
        return seq2str(names, quote="", lastsep=" or ")

    @classmethod
    def converter_for(
        cls,
        type_info: "TypeInfo",
        custom_converters: "CustomArgumentConverters|None" = None,
        languages: "Languages|None" = None,
    ) -> TypeConverter:
        info = type(type_info)(type_info.name, type(type_info.type))
        return super().converter_for(info, custom_converters, languages)

    @classmethod
    def handles(cls, type_info: "TypeInfo") -> bool:
        return type_info.type is Literal

    def no_conversion_needed(self, value: Any) -> bool:
        for info in self.type_info.nested:
            expected = info.type
            if value == expected and type(value) is type(expected):
                return True
        return False

    def _handles_value(self, value):
        return True

    def _convert(self, value):
        matches = []
        for info, converter in zip(self.type_info.nested, self.nested):
            expected = info.type
            if value == expected and type(value) is type(expected):
                return expected
            try:
                converted = converter.convert(value)
            except ValueError:
                pass
            else:
                if (
                    isinstance(expected, str)
                    and eq(converted, expected, ignore="_-")
                    or converted == expected
                ):
                    matches.append(expected)
        if len(matches) == 1:
            return matches[0]
        if matches:
            raise ValueError("No unique match found.")
        raise ValueError


@TypeConverter.register
class SecretConverter(TypeConverter):
    type = Secret
    type_name = "Secret"

    def _convert(self, value):
        raise ValueError

    def _handle_error(self, value, name, kind, error=None):
        kind = kind.capitalize() if kind.islower() else kind
        typ = type_name(value)
        if name is None:
            raise ValueError(f"{kind} must have type 'Secret', got {typ}.")
        raise ValueError(f"{kind} '{name}' must have type 'Secret', got {typ}.")


class CustomConverter(TypeConverter):

    def __init__(
        self,
        type_info: "TypeInfo",
        converter_info: "ConverterInfo",
        languages: "Languages|None" = None,
    ):
        self.converter_info = converter_info
        super().__init__(type_info, languages=languages)

    def _get_type_name(self) -> str:
        return self.converter_info.name

    @property
    def doc(self):
        return self.converter_info.doc

    @property
    def value_types(self):
        return self.converter_info.value_types

    def _handles_value(self, value):
        return not self.value_types or isinstance(value, self.value_types)

    def _convert(self, value):
        try:
            return self.converter_info.convert(value)
        except ValueError:
            raise
        except Exception:
            raise ValueError(get_error_message())


class UnknownConverter(TypeConverter):

    def convert(self, value, name=None, kind="Argument"):
        return value

    def validate(self):
        raise TypeError(f"Unrecognized type '{self.type_name}'.")

    def __bool__(self):
        return False
