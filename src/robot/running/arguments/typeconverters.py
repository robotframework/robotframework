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
from collections.abc import Container, Mapping, Sequence, Set
from datetime import datetime, date, timedelta
from decimal import InvalidOperation, Decimal
from enum import Enum
from numbers import Integral, Real
from os import PathLike
from pathlib import Path, PurePath
from typing import Any, Literal, TYPE_CHECKING, Union

from robot.conf import Languages
from robot.libraries.DateTime import convert_date, convert_time
from robot.utils import (eq, get_error_message, is_string, plural_or_not as s,
                         safe_str, seq2str, type_name)


if TYPE_CHECKING:
    from .customconverters import ConverterInfo, CustomArgumentConverters
    from .typeinfo import TypeInfo, TypedDictInfo


NoneType = type(None)


class TypeConverter:
    type = None
    type_name = None
    abc = None
    value_types = (str,)
    doc = None
    _converters = OrderedDict()

    def __init__(self, type_info: 'TypeInfo',
                 custom_converters: 'CustomArgumentConverters|None' = None,
                 languages: 'Languages|None' = None):
        self.type_info = type_info
        self.custom_converters = custom_converters
        self.languages = languages or Languages()

    @classmethod
    def register(cls, converter: 'type[TypeConverter]') -> 'type[TypeConverter]':
        cls._converters[converter.type] = converter
        return converter

    @classmethod
    def converter_for(cls, type_info: 'TypeInfo',
                      custom_converters: 'CustomArgumentConverters|None' = None,
                      languages: 'Languages|None' = None) -> 'TypeConverter|None':
        if type_info.type is None:
            return None
        if custom_converters:
            info = custom_converters.get_converter_info(type_info.type)
            if info:
                return CustomConverter(type_info, info, languages)
        if type_info.type in cls._converters:
            return cls._converters[type_info.type](type_info, custom_converters, languages)
        for converter in cls._converters.values():
            if converter.handles(type_info):
                return converter(type_info, custom_converters, languages)
        return None

    @classmethod
    def handles(cls, type_info: 'TypeInfo') -> bool:
        handled = (cls.type, cls.abc) if cls.abc else cls.type
        return isinstance(type_info.type, type) and issubclass(type_info.type, handled)

    def convert(self, value: Any,
                name: 'str|None' = None,
                kind: str = 'Argument') -> Any:
        if self.no_conversion_needed(value):
            return value
        if not self._handles_value(value):
            return self._handle_error(value, name, kind)
        try:
            if not isinstance(value, str):
                return self._non_string_convert(value)
            return self._convert(value)
        except ValueError as error:
            return self._handle_error(value, name, kind, error)

    def no_conversion_needed(self, value: Any) -> bool:
        try:
            return isinstance(value, self.type_info.type)
        except TypeError:
            # Used type wasn't a class. Compare to generic type instead.
            if self.type and self.type is not self.type_info.type:
                return isinstance(value, self.type)
            raise

    def _handles_value(self, value):
        return isinstance(value, self.value_types)

    def _non_string_convert(self, value):
        return self._convert(value)

    def _convert(self, value):
        raise NotImplementedError

    def _handle_error(self, value, name, kind, error=None):
        value_type = '' if isinstance(value, str) else f' ({type_name(value)})'
        value = safe_str(value)
        ending = f': {error}' if (error and error.args) else '.'
        if name is None:
            raise ValueError(
                f"{kind.capitalize()} '{value}'{value_type} "
                f"cannot be converted to {self.type_name}{ending}"
            )
        raise ValueError(
            f"{kind.capitalize()} '{name}' got value '{value}'{value_type} that "
            f"cannot be converted to {self.type_name}{ending}"
        )

    def _literal_eval(self, value, expected):
        if expected is set and value == 'set()':
            # `ast.literal_eval` has no way to define an empty set.
            return set()
        try:
            value = literal_eval(value)
        except (ValueError, SyntaxError):
            # Original errors aren't too informative in these cases.
            raise ValueError('Invalid expression.')
        except TypeError as err:
            raise ValueError(f'Evaluating expression failed: {err}')
        if not isinstance(value, expected):
            raise ValueError(f'Value is {type_name(value)}, not {expected.__name__}.')
        return value

    def _remove_number_separators(self, value):
        if is_string(value):
            for sep in ' ', '_':
                if sep in value:
                    value = value.replace(sep, '')
        return value


@TypeConverter.register
class EnumConverter(TypeConverter):
    type = Enum

    @property
    def type_name(self):
        return self.type_info.name

    @property
    def value_types(self):
        return (str, int) if issubclass(self.type_info.type, int) else (str,)

    def _convert(self, value):
        enum = self.type_info.type
        if isinstance(value, int):
            return self._find_by_int_value(enum, value)
        try:
            return enum[value]
        except KeyError:
            return self._find_by_normalized_name_or_int_value(enum, value)

    def _find_by_normalized_name_or_int_value(self, enum, value):
        members = sorted(enum.__members__)
        matches = [m for m in members if eq(m, value, ignore='_-')]
        if len(matches) == 1:
            return getattr(enum, matches[0])
        if len(matches) > 1:
            raise ValueError(f"{self.type_name} has multiple members matching "
                             f"'{value}'. Available: {seq2str(matches)}")
        try:
            if issubclass(self.type_info.type, int):
                return self._find_by_int_value(enum, value)
        except ValueError:
            members = [f'{m} ({getattr(enum, m)})' for m in members]
        raise ValueError(f"{self.type_name} does not have member '{value}'. "
                         f"Available: {seq2str(members)}")

    def _find_by_int_value(self, enum, value):
        value = int(value)
        for member in enum:
            if member.value == value:
                return member
        values = sorted(member.value for member in enum)
        raise ValueError(f"{self.type_name} does not have value '{value}'. "
                         f"Available: {seq2str(values)}")


@TypeConverter.register
class AnyConverter(TypeConverter):
    type = Any
    type_name = 'Any'
    value_types = (Any,)

    @classmethod
    def handles(cls, type_info: 'TypeInfo'):
        return type_info.type is Any

    def no_conversion_needed(self, value):
        return True

    def _convert(self, value):
        return value

    def _handles_value(self, value):
        return True


@TypeConverter.register
class StringConverter(TypeConverter):
    type = str
    type_name = 'string'
    value_types = (Any,)

    def _handles_value(self, value):
        return True

    def _convert(self, value):
        try:
            return str(value)
        except Exception:
            raise ValueError(get_error_message())


@TypeConverter.register
class BooleanConverter(TypeConverter):
    type = bool
    type_name = 'boolean'
    value_types = (str, int, float, NoneType)

    def _non_string_convert(self, value):
        return value

    def _convert(self, value):
        normalized = value.title()
        if normalized == 'None':
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
    type_name = 'integer'
    value_types = (str, float)

    def _non_string_convert(self, value):
        if value.is_integer():
            return int(value)
        raise ValueError('Conversion would lose precision.')

    def _convert(self, value):
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
                        raise ValueError('Conversion would lose precision.')
                    return value
            raise ValueError

    def _get_base(self, value):
        value = value.lower()
        for prefix, base in [('0x', 16), ('0o', 8), ('0b', 2)]:
            if prefix in value:
                parts = value.split(prefix)
                if len(parts) == 2 and parts[0] in ('', '-', '+'):
                    return ''.join(parts), base
        return value, 10


@TypeConverter.register
class FloatConverter(TypeConverter):
    type = float
    abc = Real
    type_name = 'float'
    value_types = (str, Real)

    def _convert(self, value):
        try:
            return float(self._remove_number_separators(value))
        except ValueError:
            raise ValueError


@TypeConverter.register
class DecimalConverter(TypeConverter):
    type = Decimal
    type_name = 'decimal'
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
    type_name = 'bytes'
    value_types = (str, bytearray)

    def _non_string_convert(self, value):
        return bytes(value)

    def _convert(self, value):
        try:
            return value.encode('latin-1')
        except UnicodeEncodeError as err:
            invalid = value[err.start:err.start+1]
            raise ValueError(f"Character '{invalid}' cannot be mapped to a byte.")


@TypeConverter.register
class ByteArrayConverter(TypeConverter):
    type = bytearray
    type_name = 'bytearray'
    value_types = (str, bytes)

    def _non_string_convert(self, value):
        return bytearray(value)

    def _convert(self, value):
        try:
            return bytearray(value, 'latin-1')
        except UnicodeEncodeError as err:
            invalid = value[err.start:err.start+1]
            raise ValueError(f"Character '{invalid}' cannot be mapped to a byte.")


@TypeConverter.register
class DateTimeConverter(TypeConverter):
    type = datetime
    type_name = 'datetime'
    value_types = (str, int, float)

    def _convert(self, value):
        return convert_date(value, result_format='datetime')


@TypeConverter.register
class DateConverter(TypeConverter):
    type = date
    type_name = 'date'

    def _convert(self, value):
        dt = convert_date(value, result_format='datetime')
        if dt.hour or dt.minute or dt.second or dt.microsecond:
            raise ValueError("Value is datetime, not date.")
        return dt.date()


@TypeConverter.register
class TimeDeltaConverter(TypeConverter):
    type = timedelta
    type_name = 'timedelta'
    value_types = (str, int, float)

    def _convert(self, value):
        return convert_time(value, result_format='timedelta')


@TypeConverter.register
class PathConverter(TypeConverter):
    type = Path
    abc = PathLike
    type_name = 'Path'
    value_types = (str, PurePath)

    def _convert(self, value):
        return Path(value)


@TypeConverter.register
class NoneConverter(TypeConverter):
    type = NoneType
    type_name = 'None'

    @classmethod
    def handles(cls, type_info: 'TypeInfo') -> bool:
        return type_info.type in (NoneType, None)

    def _convert(self, value):
        if value.upper() == 'NONE':
            return None
        raise ValueError


@TypeConverter.register
class ListConverter(TypeConverter):
    type = list
    type_name = 'list'
    abc = Sequence
    value_types = (str, Sequence)

    def __init__(self, type_info: 'TypeInfo',
                 custom_converters: 'CustomArgumentConverters|None' = None,
                 languages: 'Languages|None' = None):
        super().__init__(type_info, custom_converters, languages)
        nested = type_info.nested
        if not nested:
            self.converter = None
        else:
            self.type_name = str(type_info)
            self.converter = self.converter_for(nested[0], custom_converters, languages)

    def no_conversion_needed(self, value):
        if isinstance(value, str) or not super().no_conversion_needed(value):
            return False
        if not self.converter:
            return True
        return all(self.converter.no_conversion_needed(v) for v in value)

    def _non_string_convert(self, value):
        return self._convert_items(list(value))

    def _convert(self, value):
        return self._convert_items(self._literal_eval(value, list))

    def _convert_items(self, value):
        if not self.converter:
            return value
        return [self.converter.convert(v, name=i, kind='Item')
                for i, v in enumerate(value)]


@TypeConverter.register
class TupleConverter(TypeConverter):
    type = tuple
    type_name = 'tuple'
    value_types = (str, Sequence)

    def __init__(self, type_info: 'TypeInfo',
                 custom_converters: 'CustomArgumentConverters|None' = None,
                 languages: 'Languages|None' = None):
        super().__init__(type_info, custom_converters, languages)
        self.converters = ()
        self.homogenous = False
        nested = type_info.nested
        if not nested:
            return
        if nested[-1].type is Ellipsis:
            nested = nested[:-1]
            if len(nested) != 1:
                raise TypeError(f'Homogenous tuple used as a type hint requires '
                                f'exactly one nested type, got {len(nested)}.')
            self.homogenous = True
        self.type_name = str(type_info)
        self.converters = tuple(self.converter_for(t, custom_converters, languages)
                                or NullConverter() for t in nested)

    def no_conversion_needed(self, value):
        if isinstance(value, str) or not super().no_conversion_needed(value):
            return False
        if not self.converters:
            return True
        if self.homogenous:
            return all(self.converters[0].no_conversion_needed(v) for v in value)
        if len(value) != len(self.converters):
            return False
        return all(c.no_conversion_needed(v) for c, v in zip(self.converters, value))

    def _non_string_convert(self, value):
        return self._convert_items(tuple(value))

    def _convert(self, value):
        return self._convert_items(self._literal_eval(value, tuple))

    def _convert_items(self, value):
        if not self.converters:
            return value
        if self.homogenous:
            conv = self.converters[0]
            return tuple(conv.convert(v, name=str(i), kind='Item')
                         for i, v in enumerate(value))
        if len(self.converters) != len(value):
            raise ValueError(f'Expected {len(self.converters)} '
                             f'item{s(self.converters)}, got {len(value)}.')
        return tuple(conv.convert(v, name=str(i), kind='Item')
                     for i, (conv, v) in enumerate(zip(self.converters, value)))


@TypeConverter.register
class TypedDictConverter(TypeConverter):
    type = 'TypedDict'
    value_types = (str, Mapping)
    type_info: 'TypedDictInfo'

    def __init__(self, type_info: 'TypedDictInfo',
                 custom_converters: 'CustomArgumentConverters|None' = None,
                 languages: 'Languages|None' = None):
        super().__init__(type_info, custom_converters, languages)
        self.converters = {n: self.converter_for(t, custom_converters, languages)
                           for n, t in type_info.annotations.items()}
        self.type_name = type_info.name

    @classmethod
    def handles(cls, type_info: 'TypeInfo') -> bool:
        return type_info.is_typed_dict

    def no_conversion_needed(self, value):
        return False

    def _non_string_convert(self, value):
        return self._convert_items(value)

    def _convert(self, value):
        return self._convert_items(self._literal_eval(value, dict))

    def _convert_items(self, value):
        not_allowed = []
        for key in value:
            try:
                converter = self.converters[key]
            except KeyError:
                not_allowed.append(key)
            else:
                if converter:
                    value[key] = converter.convert(value[key], name=key, kind='Item')
        if not_allowed:
            error = f'Item{s(not_allowed)} {seq2str(sorted(not_allowed))} not allowed.'
            available = [key for key in self.converters if key not in value]
            if available:
                error += f' Available item{s(available)}: {seq2str(sorted(available))}'
            raise ValueError(error)
        missing = [key for key in self.type_info.required if key not in value]
        if missing:
            raise ValueError(f"Required item{s(missing)} "
                             f"{seq2str(sorted(missing))} missing.")
        return value


@TypeConverter.register
class DictionaryConverter(TypeConverter):
    type = dict
    abc = Mapping
    type_name = 'dictionary'
    value_types = (str, Mapping)

    def __init__(self, type_info: 'TypeInfo',
                 custom_converters: 'CustomArgumentConverters|None' = None,
                 languages: 'Languages|None' = None):
        super().__init__(type_info, custom_converters, languages)
        nested = type_info.nested
        if not nested:
            self.converters = ()
        else:
            self.type_name = str(type_info)
            self.converters = tuple(self.converter_for(t, custom_converters, languages)
                                    or NullConverter() for t in nested)

    def no_conversion_needed(self, value):
        if isinstance(value, str) or not super().no_conversion_needed(value):
            return False
        if not self.converters:
            return True
        no_key_conversion_needed = self.converters[0].no_conversion_needed
        no_value_conversion_needed = self.converters[1].no_conversion_needed
        return all(no_key_conversion_needed(k) and no_value_conversion_needed(v)
                   for k, v in value.items())

    def _non_string_convert(self, value):
        if self._used_type_is_dict() and not isinstance(value, dict):
            value = dict(value)
        return self._convert_items(value)

    def _used_type_is_dict(self):
        return issubclass(self.type_info.type, dict)

    def _convert(self, value):
        return self._convert_items(self._literal_eval(value, dict))

    def _convert_items(self, value):
        if not self.converters:
            return value
        convert_key = self._get_converter(self.converters[0], 'Key')
        convert_value = self._get_converter(self.converters[1], 'Item')
        return {convert_key(None, k): convert_value(k, v) for k, v in value.items()}

    def _get_converter(self, converter, kind):
        return lambda name, value: converter.convert(value, name, kind=kind)


@TypeConverter.register
class SetConverter(TypeConverter):
    type = set
    abc = Set
    type_name = 'set'
    value_types = (str, Container)

    def __init__(self, type_info: 'TypeInfo',
                 custom_converters: 'CustomArgumentConverters|None' = None,
                 languages: 'Languages|None' = None):
        super().__init__(type_info, custom_converters, languages)
        nested = type_info.nested
        if not nested:
            self.converter = None
        else:
            self.type_name = str(type_info)
            self.converter = self.converter_for(nested[0], custom_converters, languages)

    def no_conversion_needed(self, value):
        if isinstance(value, str) or not super().no_conversion_needed(value):
            return False
        if not self.converter:
            return True
        return all(self.converter.no_conversion_needed(v) for v in value)

    def _non_string_convert(self, value):
        return self._convert_items(set(value))

    def _convert(self, value):
        return self._convert_items(self._literal_eval(value, set))

    def _convert_items(self, value):
        if not self.converter:
            return value
        return {self.converter.convert(v, kind='Item') for v in value}


@TypeConverter.register
class FrozenSetConverter(SetConverter):
    type = frozenset
    type_name = 'frozenset'

    def _non_string_convert(self, value):
        return frozenset(super()._non_string_convert(value))

    def _convert(self, value):
        # There are issues w/ literal_eval. See self._literal_eval for details.
        if value == 'frozenset()':
            return frozenset()
        return frozenset(super()._convert(value))


@TypeConverter.register
class UnionConverter(TypeConverter):
    type = Union

    def __init__(self, type_info: 'TypeInfo',
                 custom_converters: 'CustomArgumentConverters|None' = None,
                 languages: 'Languages|None' = None):
        super().__init__(type_info, custom_converters, languages)
        self.converters = tuple(self.converter_for(info, custom_converters, languages)
                                for info in type_info.nested)
        if not self.converters:
            raise TypeError('Union used as a type hint cannot be empty.')

    @property
    def type_name(self):
        if not self.converters:
            return 'Union'
        return seq2str([c.type_name for c in self.converters], quote='', lastsep=' or ')

    @classmethod
    def handles(cls, type_info: 'TypeInfo') -> bool:
        return type_info.is_union

    def _handles_value(self, value):
        return True

    def no_conversion_needed(self, value):
        for converter, info in zip(self.converters, self.type_info.nested):
            if converter:
                if converter.no_conversion_needed(value):
                    return True
            else:
                try:
                    if isinstance(value, info.type):
                        return True
                except TypeError:
                    pass
        return False

    def _convert(self, value):
        unrecognized_types = False
        for converter in self.converters:
            if converter:
                try:
                    return converter.convert(value)
                except ValueError:
                    pass
            else:
                unrecognized_types = True
        if unrecognized_types:
            return value
        raise ValueError


@TypeConverter.register
class LiteralConverter(TypeConverter):
    type = Literal
    type_name = 'Literal'
    value_types = (Any,)

    def __init__(self, type_info: 'TypeInfo',
                 custom_converters: 'CustomArgumentConverters|None' = None,
                 languages: 'Languages|None' = None):
        super().__init__(type_info, custom_converters, languages)
        self.converters = [(info.type, self.literal_converter_for(info, languages))
                           for info in type_info.nested]
        self.type_name = seq2str([info.name for info in type_info.nested],
                                 quote='', lastsep=' or ')

    def literal_converter_for(self, type_info: 'TypeInfo',
                              languages: 'Languages|None' = None) -> TypeConverter:
        type_info = type(type_info)(type_info.name, type(type_info.type))
        return self.converter_for(type_info, languages=languages)

    @classmethod
    def handles(cls, type_info: 'TypeInfo') -> bool:
        return type_info.type is Literal

    def no_conversion_needed(self, value: Any) -> bool:
        return False

    def _handles_value(self, value):
        return True

    def _convert(self, value):
        matches = []
        for expected, converter in self.converters:
            if value == expected and type(value) is type(expected):
                return expected
            try:
                converted = converter.convert(value)
            except ValueError:
                pass
            else:
                if (isinstance(expected, str) and eq(converted, expected, ignore='_-')
                        or converted == expected):
                    matches.append(expected)
        if len(matches) == 1:
            return matches[0]
        if matches:
            raise ValueError('No unique match found.')
        raise ValueError


class CustomConverter(TypeConverter):

    def __init__(self, type_info: 'TypeInfo',
                 converter_info: 'ConverterInfo',
                 languages: 'Languages|None' = None):
        super().__init__(type_info, languages=languages)
        self.converter_info = converter_info

    @property
    def type_name(self):
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


class NullConverter:

    def convert(self, value, name, kind='Argument'):
        return value

    def no_conversion_needed(self, value):
        return True
