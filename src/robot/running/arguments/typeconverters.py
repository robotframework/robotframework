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
from collections.abc import ByteString, Container, Mapping, Sequence, Set
from datetime import datetime, date, timedelta
from decimal import InvalidOperation, Decimal
from enum import Enum
from numbers import Integral, Real
from os import PathLike
from pathlib import Path, PurePath
from typing import Any, Tuple, TypeVar, Union

from robot.conf import Languages
from robot.libraries.DateTime import convert_date, convert_time
from robot.utils import (eq, get_error_message, has_args, is_string, is_union,
                         plural_or_not as s, safe_str, seq2str, type_name, type_repr,
                         typeddict_types)


NoneType = type(None)


class TypeConverter:
    type = None
    type_name = None
    abc = None
    aliases = ()
    value_types = (str,)
    doc = None
    _converters = OrderedDict()
    _type_aliases = {}

    def __init__(self, used_type, custom_converters=None, languages=None):
        self.used_type = used_type
        self.custom_converters = custom_converters
        self.languages = languages or Languages()

    @classmethod
    def register(cls, converter):
        cls._converters[converter.type] = converter
        for name in (converter.type_name,) + converter.aliases:
            if name is not None and not isinstance(name, property):
                cls._type_aliases[name.lower()] = converter.type
        return converter

    @classmethod
    def converter_for(cls, type_, custom_converters=None, languages=None):
        try:
            hash(type_)
        except TypeError:
            return None
        if isinstance(type_, str):
            try:
                type_ = cls._type_aliases[type_.lower()]
            except KeyError:
                return None
        used_type = type_
        if getattr(type_, '__origin__', None) and type_.__origin__ is not Union:
            type_ = type_.__origin__
        if custom_converters:
            info = custom_converters.get_converter_info(type_)
            if info:
                return CustomConverter(used_type, info)
        if type_ in cls._converters:
            return cls._converters[type_](used_type, custom_converters, languages)
        for converter in cls._converters.values():
            if converter.handles(type_):
                return converter(used_type, custom_converters, languages)
        return None

    @classmethod
    def handles(cls, type_):
        handled = (cls.type, cls.abc) if cls.abc else cls.type
        return isinstance(type_, type) and issubclass(type_, handled)

    def convert(self, name, value, explicit_type=True, strict=True, kind='Argument'):
        if self.no_conversion_needed(value):
            return value
        if not self._handles_value(value):
            return self._handle_error(name, value, kind, strict=strict)
        try:
            if not isinstance(value, str):
                return self._non_string_convert(value, explicit_type)
            return self._convert(value, explicit_type)
        except ValueError as error:
            return self._handle_error(name, value, kind, error, strict)

    def no_conversion_needed(self, value):
        used_type = getattr(self.used_type, '__origin__', self.used_type)
        try:
            return isinstance(value, used_type)
        except TypeError:
            # Used type wasn't a class. Compare to generic type instead.
            if self.type and self.type is not self.used_type:
                return isinstance(value, self.type)
            raise

    def _handles_value(self, value):
        return isinstance(value, self.value_types)

    def _non_string_convert(self, value, explicit_type=True):
        return self._convert(value, explicit_type)

    def _convert(self, value, explicit_type=True):
        raise NotImplementedError

    def _handle_error(self, name, value, kind, error=None, strict=True):
        if not strict:
            return value
        value_type = '' if isinstance(value, str) else f' ({type_name(value)})'
        value = safe_str(value)
        ending = f': {error}' if (error and error.args) else '.'
        if name is None:
            raise ValueError(
                f"{kind} '{value}'{value_type} "
                f"cannot be converted to {self.type_name}{ending}"
            )
        raise ValueError(
            f"{kind} '{name}' got value '{value}'{value_type} that "
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

    def _get_nested_types(self, type_hint, expected_count=None):
        types = getattr(type_hint, '__args__', ())
        # With generics from typing like Dict, __args__ is None with Python 3.6 and
        # contains TypeVars with 3.7-3.8. Newer versions don't have __args__ at all.
        # Subscripted usages like Dict[x, y].__args__ work fine with all.
        if not types or all(isinstance(a, TypeVar) for a in types):
            return ()
        if expected_count and len(types) != expected_count:
            raise TypeError(f'{type_hint.__name__}[] construct used as a type hint '
                            f'requires exactly {expected_count} nested '
                            f'type{s(expected_count)}, got {len(types)}.')
        return types

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
        return self.used_type.__name__

    @property
    def value_types(self):
        return (str, int) if issubclass(self.used_type, int) else (str,)

    def _convert(self, value, explicit_type=True):
        enum = self.used_type
        if isinstance(value, int):
            return self._find_by_int_value(enum, value)
        try:
            return enum[value]
        except KeyError:
            return self._find_by_normalized_name_or_int_value(enum, value)

    def _find_by_normalized_name_or_int_value(self, enum, value):
        members = sorted(enum.__members__)
        matches = [m for m in members if eq(m, value, ignore='_')]
        if len(matches) == 1:
            return getattr(enum, matches[0])
        if len(matches) > 1:
            raise ValueError(f"{self.type_name} has multiple members matching "
                             f"'{value}'. Available: {seq2str(matches)}")
        try:
            if issubclass(self.used_type, int):
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
    aliases = ('any',)
    value_types = (Any,)

    @classmethod
    def handles(cls, type_):
        return type_ is Any

    def no_conversion_needed(self, value):
        return True

    def _convert(self, value, explicit_type=True):
        return value

    def _handles_value(self, value):
        return True


@TypeConverter.register
class StringConverter(TypeConverter):
    type = str
    type_name = 'string'
    aliases = ('string', 'str', 'unicode')
    value_types = (Any,)

    def _handles_value(self, value):
        return True

    def _convert(self, value, explicit_type=True):
        if not explicit_type:
            return value
        try:
            return str(value)
        except Exception:
            raise ValueError(get_error_message())


@TypeConverter.register
class BooleanConverter(TypeConverter):
    type = bool
    type_name = 'boolean'
    aliases = ('bool',)
    value_types = (str, int, float, NoneType)

    def _non_string_convert(self, value, explicit_type=True):
        return value

    def _convert(self, value, explicit_type=True):
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
    aliases = ('int', 'long')
    value_types = (str, float)

    def _non_string_convert(self, value, explicit_type=True):
        if value.is_integer():
            return int(value)
        raise ValueError('Conversion would lose precision.')

    def _convert(self, value, explicit_type=True):
        value = self._remove_number_separators(value)
        value, base = self._get_base(value)
        try:
            return int(value, base)
        except ValueError:
            if base == 10 and not explicit_type:
                try:
                    return float(value)
                except ValueError:
                    pass
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
    aliases = ('double',)
    value_types = (str, Real)

    def _convert(self, value, explicit_type=True):
        try:
            return float(self._remove_number_separators(value))
        except ValueError:
            raise ValueError


@TypeConverter.register
class DecimalConverter(TypeConverter):
    type = Decimal
    type_name = 'decimal'
    value_types = (str, int, float)

    def _convert(self, value, explicit_type=True):
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
    abc = ByteString
    type_name = 'bytes'
    value_types = (str, bytearray)

    def _non_string_convert(self, value, explicit_type=True):
        return bytes(value)

    def _convert(self, value, explicit_type=True):
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

    def _non_string_convert(self, value, explicit_type=True):
        return bytearray(value)

    def _convert(self, value, explicit_type=True):
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

    def _convert(self, value, explicit_type=True):
        return convert_date(value, result_format='datetime')


@TypeConverter.register
class DateConverter(TypeConverter):
    type = date
    type_name = 'date'

    def _convert(self, value, explicit_type=True):
        dt = convert_date(value, result_format='datetime')
        if dt.hour or dt.minute or dt.second or dt.microsecond:
            raise ValueError("Value is datetime, not date.")
        return dt.date()


@TypeConverter.register
class TimeDeltaConverter(TypeConverter):
    type = timedelta
    type_name = 'timedelta'
    value_types = (str, int, float)

    def _convert(self, value, explicit_type=True):
        return convert_time(value, result_format='timedelta')


@TypeConverter.register
class PathConverter(TypeConverter):
    type = Path
    abc = PathLike
    type_name = 'Path'
    value_types = (str, PurePath)

    def _convert(self, value, explicit_type=True):
        return Path(value)


@TypeConverter.register
class NoneConverter(TypeConverter):
    type = NoneType
    type_name = 'None'

    @classmethod
    def handles(cls, type_):
        return type_ in (NoneType, None)

    def _convert(self, value, explicit_type=True):
        if value.upper() == 'NONE':
            return None
        raise ValueError


@TypeConverter.register
class ListConverter(TypeConverter):
    type = list
    type_name = 'list'
    abc = Sequence
    value_types = (str, Sequence)

    def __init__(self, used_type, custom_converters=None, languages=None):
        super().__init__(used_type, custom_converters, languages)
        types = self._get_nested_types(used_type, expected_count=1)
        if not types:
            self.converter = None
        else:
            self.type_name = type_repr(used_type)
            self.converter = self.converter_for(types[0], custom_converters, languages)

    @classmethod
    def handles(cls, type_):
        # `type_ is not Tuple` is needed with Python 3.6.
        return super().handles(type_) and type_ is not Tuple

    def no_conversion_needed(self, value):
        if isinstance(value, str) or not super().no_conversion_needed(value):
            return False
        if not self.converter:
            return True
        return all(self.converter.no_conversion_needed(v) for v in value)

    def _non_string_convert(self, value, explicit_type=True):
        return self._convert_items(list(value), explicit_type)

    def _convert(self, value, explicit_type=True):
        return self._convert_items(self._literal_eval(value, list), explicit_type)

    def _convert_items(self, value, explicit_type):
        if not self.converter:
            return value
        return [self.converter.convert(i, v, explicit_type, kind='Item')
                for i, v in enumerate(value)]


@TypeConverter.register
class TupleConverter(TypeConverter):
    type = tuple
    type_name = 'tuple'
    value_types = (str, Sequence)

    def __init__(self, used_type, custom_converters=None, languages=None):
        super().__init__(used_type, custom_converters, languages)
        self.converters = ()
        self.homogenous = False
        types = self._get_nested_types(used_type)
        if not types:
            return
        if types[-1] is Ellipsis:
            types = types[:-1]
            if len(types) != 1:
                raise TypeError(f'Homogenous tuple used as a type hint requires '
                                f'exactly one nested type, got {len(types)}.')
            self.homogenous = True
        self.type_name = type_repr(used_type)
        self.converters = tuple(self.converter_for(t, custom_converters, languages)
                                or NullConverter() for t in types)

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

    def _non_string_convert(self, value, explicit_type=True):
        return self._convert_items(tuple(value), explicit_type)

    def _convert(self, value, explicit_type=True):
        return self._convert_items(self._literal_eval(value, tuple), explicit_type)

    def _convert_items(self, value, explicit_type):
        if not self.converters:
            return value
        if self.homogenous:
            conv = self.converters[0]
            return tuple(conv.convert(str(i), v, explicit_type, kind='Item')
                         for i, v in enumerate(value))
        if len(self.converters) != len(value):
            raise ValueError(f'Expected {len(self.converters)} '
                             f'item{s(self.converters)}, got {len(value)}.')
        return tuple(conv.convert(i, v, explicit_type, kind='Item')
                     for i, (conv, v) in enumerate(zip(self.converters, value)))


@TypeConverter.register
class TypedDictConverter(TypeConverter):
    type = 'TypedDict'
    value_types = (str, Mapping)

    def __init__(self, used_type, custom_converters, languages=None):
        super().__init__(used_type, custom_converters, languages)
        self.converters = {n: self.converter_for(t, custom_converters, languages)
                           for n, t in used_type.__annotations__.items()}
        self.type_name = used_type.__name__
        # __required_keys__ is new in Python 3.9.
        self.required_keys = getattr(used_type, '__required_keys__', frozenset())

    @classmethod
    def handles(cls, type_):
        return isinstance(type_, typeddict_types)

    def no_conversion_needed(self, value):
        return False

    def _non_string_convert(self, value, explicit_type=True):
        return self._convert_items(value)

    def _convert(self, value, explicit_type=True):
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
                    value[key] = converter.convert(key, value[key], kind='Item')
        if not_allowed:
            error = f'Item{s(not_allowed)} {seq2str(sorted(not_allowed))} not allowed.'
            available = [key for key in self.converters if key not in value]
            if available:
                error += f' Available item{s(available)}: {seq2str(sorted(available))}'
            raise ValueError(error)
        missing = [key for key in self.required_keys if key not in value]
        if missing:
            raise ValueError(f"Required item{s(missing)} "
                             f"{seq2str(sorted(missing))} missing.")
        return value


@TypeConverter.register
class DictionaryConverter(TypeConverter):
    type = dict
    abc = Mapping
    type_name = 'dictionary'
    aliases = ('dict', 'map')
    value_types = (str, Mapping)

    def __init__(self, used_type, custom_converters=None, languages=None):
        super().__init__(used_type, custom_converters, languages)
        types = self._get_nested_types(used_type, expected_count=2)
        if not types:
            self.converters = ()
        else:
            self.type_name = type_repr(used_type)
            self.converters = tuple(self.converter_for(t, custom_converters, languages)
                                    or NullConverter() for t in types)

    def no_conversion_needed(self, value):
        if isinstance(value, str) or not super().no_conversion_needed(value):
            return False
        if not self.converters:
            return True
        no_key_conversion_needed = self.converters[0].no_conversion_needed
        no_value_conversion_needed = self.converters[1].no_conversion_needed
        return all(no_key_conversion_needed(k) and no_value_conversion_needed(v)
                   for k, v in value.items())

    def _non_string_convert(self, value, explicit_type=True):
        if self._used_type_is_dict() and not isinstance(value, dict):
            value = dict(value)
        return self._convert_items(value, explicit_type)

    def _used_type_is_dict(self):
        used_type = getattr(self.used_type, '__origin__', self.used_type)
        return issubclass(used_type, dict)

    def _convert(self, value, explicit_type=True):
        return self._convert_items(self._literal_eval(value, dict), explicit_type)

    def _convert_items(self, value, explicit_type):
        if not self.converters:
            return value
        convert_key = self._get_converter(self.converters[0], explicit_type, 'Key')
        convert_value = self._get_converter(self.converters[1], explicit_type, 'Item')
        return {convert_key(None, k): convert_value(k, v) for k, v in value.items()}

    def _get_converter(self, converter, explicit_type, kind):
        return lambda name, value: converter.convert(name, value, explicit_type,
                                                     kind=kind)


@TypeConverter.register
class SetConverter(TypeConverter):
    type = set
    abc = Set
    type_name = 'set'
    value_types = (str, Container)

    def __init__(self, used_type, custom_converters=None, languages=None):
        super().__init__(used_type, custom_converters, languages)
        types = self._get_nested_types(used_type, expected_count=1)
        if not types:
            self.converter = None
        else:
            self.type_name = type_repr(used_type)
            self.converter = self.converter_for(types[0], custom_converters, languages)

    def no_conversion_needed(self, value):
        if isinstance(value, str) or not super().no_conversion_needed(value):
            return False
        if not self.converter:
            return True
        return all(self.converter.no_conversion_needed(v) for v in value)

    def _non_string_convert(self, value, explicit_type=True):
        return self._convert_items(set(value), explicit_type)

    def _convert(self, value, explicit_type=True):
        return self._convert_items(self._literal_eval(value, set), explicit_type)

    def _convert_items(self, value, explicit_type):
        if not self.converter:
            return value
        return {self.converter.convert(None, v, explicit_type, kind='Item')
                for v in value}


@TypeConverter.register
class FrozenSetConverter(SetConverter):
    type = frozenset
    type_name = 'frozenset'

    def _non_string_convert(self, value, explicit_type=True):
        return frozenset(super()._non_string_convert(value, explicit_type))

    def _convert(self, value, explicit_type=True):
        # There are issues w/ literal_eval. See self._literal_eval for details.
        if value == 'frozenset()':
            return frozenset()
        return frozenset(super()._convert(value, explicit_type))


@TypeConverter.register
class CombinedConverter(TypeConverter):
    type = Union

    def __init__(self, union, custom_converters, languages=None):
        super().__init__(self._get_types(union))
        self.converters = tuple(self.converter_for(t, custom_converters, languages)
                                for t in self.used_type)

    def _get_types(self, union):
        if not union:
            return ()
        if isinstance(union, tuple):
            return union
        if has_args(union):
            return union.__args__
        return ()

    @property
    def type_name(self):
        if not self.used_type:
            return 'union'
        return ' or '.join(type_name(t) for t in self.used_type)

    @classmethod
    def handles(cls, type_):
        return is_union(type_, allow_tuple=True)

    def _handles_value(self, value):
        return True

    def no_conversion_needed(self, value):
        for converter, type_ in zip(self.converters, self.used_type):
            if converter:
                if converter.no_conversion_needed(value):
                    return True
            else:
                try:
                    if isinstance(value, type_):
                        return True
                except TypeError:
                    pass
        return False

    def _convert(self, value, explicit_type=True):
        if not self.used_type:
            raise ValueError('Cannot have union without types.')
        unrecognized_types = False
        for converter in self.converters:
            if converter:
                try:
                    return converter.convert('', value, explicit_type)
                except ValueError:
                    pass
            else:
                unrecognized_types = True
        if unrecognized_types:
            return value
        raise ValueError


class CustomConverter(TypeConverter):

    def __init__(self, used_type, converter_info, languages=None):
        super().__init__(used_type, languages=languages)
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

    def _convert(self, value, explicit_type=True):
        try:
            return self.converter_info.convert(value)
        except ValueError:
            raise
        except Exception:
            raise ValueError(get_error_message())


class NullConverter:

    def convert(self, name, value, explicit_type=True, strict=True, kind='Argument'):
        return value

    def no_conversion_needed(self, value):
        return True
