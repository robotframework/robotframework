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
try:
    from collections import abc
except ImportError:    # Python 2
    import collections as abc
from datetime import datetime, date, timedelta
from decimal import InvalidOperation, Decimal
try:
    from enum import Enum
except ImportError:    # Standard in Py 3.4+ but can be separately installed
    class Enum(object):
        pass
from numbers import Integral, Real

from robot.libraries.DateTime import convert_date, convert_time
from robot.utils import FALSE_STRINGS, TRUE_STRINGS, PY2, unicode


class TypeConverter(object):
    type = None
    abc = None
    convert_none = True
    _converters = OrderedDict()

    @property
    def type_name(self):
        return self.type.__name__.lower()

    @classmethod
    def register(cls, converter_class):
        cls._converters[converter_class.type] = converter_class()
        return converter_class

    @classmethod
    def converter_for(cls, type_):
        if issubclass(type_, unicode) or not isinstance(type_, type):
            return None
        if type_ in cls._converters:
            return cls._converters[type_]
        for converter in cls._converters.values():
            if converter.handles(type_):
                return converter.get_converter(type_)
        return None

    def handles(self, type_):
        return (issubclass(type_, self.type) or
                self.abc and issubclass(type_, self.abc))

    def get_converter(self, type_):
        return self

    def convert(self, name, value, explicit_type=True):
        if self.convert_none and value.upper() == 'NONE':
            return None
        try:
            return self._convert(value, explicit_type)
        except ValueError:
            return self._handle_error(name, value, explicit_type)

    def _convert(self, value, explicit_type=True):
        raise NotImplementedError

    def _handle_error(self, name, value, explicit_type=True):
        if explicit_type:
            raise ValueError("Argument '%s' cannot be converted to %s, "
                             "got '%s'." % (name, self.type_name, value))
        return value

    def _literal_eval(self, value, expected):
        # ast.literal_eval has some issues with sets:
        if expected is set:
            # On Python 2 it doesn't handle sets at all.
            if PY2:
                raise ValueError    # FIXME: Better error reporting needed
            # There is no way to define an empty set.
            if value == 'set()':
                return set()
        try:
            value = literal_eval(value)
        except (SyntaxError, TypeError):
            raise ValueError
        if not isinstance(value, expected):
            raise ValueError
        return value


@TypeConverter.register
class BooleanConverter(TypeConverter):
    type = bool
    type_name = 'boolean'

    def _convert(self, value, explicit_type=True):
        upper = value.upper()
        if upper in TRUE_STRINGS:
            return True
        if upper in FALSE_STRINGS:
            return False
        return value


@TypeConverter.register
class IntegerConverter(TypeConverter):
    type = int
    abc = Integral
    type_name = 'integer'

    def _convert(self, value, explicit_type=True):
        try:
            return int(value)
        except ValueError:
            if explicit_type:
                raise
            return float(value)


@TypeConverter.register
class FloatConverter(TypeConverter):
    type = float
    abc = Real

    def _convert(self, value, explicit_type=True):
        return float(value)


@TypeConverter.register
class DecimalConverter(TypeConverter):
    type = Decimal

    def _convert(self, value, explicit_type=True):
        try:
            return Decimal(value)
        except InvalidOperation:
            raise ValueError


@TypeConverter.register
class BytesConverter(TypeConverter):
    type = bytes
    abc = getattr(abc, 'ByteString', None)    # ByteString is new in Python 3
    type_name = 'bytes'                       # Needed on Python 2
    convert_none = False

    def _convert(self, value, explicit_type=True):
        if PY2 and not explicit_type:
            return value
        try:
            return value.encode('latin-1')
        except UnicodeEncodeError:
            raise ValueError


@TypeConverter.register
class ByteArrayConverter(TypeConverter):
    type = bytearray
    convert_none = False

    def _convert(self, value, explicit_type=True):
        try:
            return bytearray(value, 'latin-1')
        except UnicodeEncodeError:
            raise ValueError


@TypeConverter.register
class DateTimeConverter(TypeConverter):
    type = datetime

    def _convert(self, value, explicit_type=True):
        return convert_date(value, result_format='datetime')


@TypeConverter.register
class DateConverter(TypeConverter):
    type = date

    def _convert(self, value, explicit_type=True):
        dt = convert_date(value, result_format='datetime')
        if dt.hour or dt.minute or dt.second or dt.microsecond:
            raise ValueError
        return dt.date()


@TypeConverter.register
class TimeDeltaConverter(TypeConverter):
    type = timedelta

    def _convert(self, value, explicit_type=True):
        return convert_time(value, result_format='timedelta')


@TypeConverter.register
class NoneConverter(TypeConverter):
    type = type(None)

    def _convert(self, value, explicit_type=True):
        return value


@TypeConverter.register
class ListConverter(TypeConverter):
    type = list
    abc = abc.MutableSequence

    def _convert(self, value, explicit_type=True):
        return self._literal_eval(value, list)


@TypeConverter.register
class TupleConverter(TypeConverter):
    type = tuple

    def _convert(self, value, explicit_type=True):
        return self._literal_eval(value, tuple)


@TypeConverter.register
class DictionaryConverter(TypeConverter):
    type = dict
    abc = abc.Mapping
    type_name = 'dictionary'

    def _convert(self, value, explicit_type=True):
        return self._literal_eval(value, dict)


@TypeConverter.register
class SetConverter(TypeConverter):
    type = set
    abc = abc.Set

    def _convert(self, value, explicit_type=True):
        return self._literal_eval(value, set)


@TypeConverter.register
class FrozenSetConverter(TypeConverter):
    type = frozenset
    type_name = 'set'

    def _convert(self, value, explicit_type=True):
        # There are issues w/ literal_eval. See self._literal_eval for details.
        if value == 'frozenset()' and not PY2:
            return frozenset()
        return frozenset(self._literal_eval(value, set))


@TypeConverter.register
class SequenceConverter(TypeConverter):
    type = abc.Sequence

    def _convert(self, value, explicit_type=True):
        for type_ in [list, tuple]:
            try:
                return self._literal_eval(value, type_)
            except ValueError:
                pass
        raise ValueError


@TypeConverter.register
class IterableConverter(TypeConverter):
    type = abc.Iterable

    def _convert(self, value, explicit_type=True):
        for type_ in [list, tuple, set, dict]:
            try:
                return self._literal_eval(value, type_)
            except ValueError:
                pass
        raise ValueError


@TypeConverter.register
class EnumConverter(TypeConverter):
    type = Enum

    def __init__(self, enum=None):
        self._enum = enum

    @property
    def type_name(self):
        return self._enum.__name__ if self._enum else 'enum'

    def get_converter(self, type_):
        return EnumConverter(type_)

    def _convert(self, value, explicit_type=True):
        try:
            return self._enum[value]
        except KeyError:
            raise ValueError
