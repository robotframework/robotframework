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
from robot.utils import (FALSE_STRINGS, IRONPYTHON, TRUE_STRINGS, PY_VERSION,
                         PY2, seq2str, type_name, unicode)


class TypeConverter(object):
    type = None
    abc = None
    aliases = ()
    convert_none = True
    _converters = OrderedDict()
    _type_aliases = {}

    @property
    def type_name(self):
        return self.type.__name__.lower()

    @classmethod
    def register(cls, converter_class):
        converter = converter_class()
        cls._converters[converter.type] = converter
        for name in (converter.type_name,) + converter.aliases:
            if name is not None:
                cls._type_aliases[name.lower()] = converter.type
        return converter_class

    @classmethod
    def converter_for(cls, type_):
        # Types defined in the typing module in Python 3.7+. For details see
        # https://bugs.python.org/issue34568
        if PY_VERSION >= (3, 7) and hasattr(type_, '__origin__'):
            type_ = type_.__origin__
        if isinstance(type_, (str, unicode)):
            try:
                type_ = cls._type_aliases[type_.lower()]
            except KeyError:
                return None
        if not isinstance(type_, type) or issubclass(type_, unicode):
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
        except ValueError as error:
            return self._handle_error(name, value, error, explicit_type)

    def _convert(self, value, explicit_type=True):
        raise NotImplementedError

    def _handle_error(self, name, value, error, explicit_type=True):
        if not explicit_type:
            return value
        ending = u': %s' % error if error.args else '.'
        raise ValueError("Argument '%s' got value '%s' that cannot be "
                         "converted to %s%s"
                         % (name, value, self.type_name, ending))

    def _literal_eval(self, value, expected):
        # ast.literal_eval has some issues with sets:
        if expected is set:
            # On Python 2 it doesn't handle sets at all.
            if PY2:
                raise ValueError('Sets are not supported on Python 2.')
            # There is no way to define an empty set.
            if value == 'set()':
                return set()
        try:
            value = literal_eval(value)
        except (ValueError, SyntaxError):
            # Original errors aren't too informative in these cases.
            raise ValueError('Invalid expression.')
        except TypeError as err:
            raise ValueError('Evaluating expression failed: %s' % err)
        if not isinstance(value, expected):
            raise ValueError('Value is %s, not %s.' % (type_name(value),
                                                       expected.__name__))
        return value


@TypeConverter.register
class BooleanConverter(TypeConverter):
    type = bool
    type_name = 'boolean'
    aliases = ('bool',)

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
    aliases = ('int', 'long')

    def _convert(self, value, explicit_type=True):
        try:
            return int(value)
        except ValueError:
            if not explicit_type:
                try:
                    return float(value)
                except ValueError:
                    pass
        raise ValueError


@TypeConverter.register
class FloatConverter(TypeConverter):
    type = float
    abc = Real
    aliases = ('double',)

    def _convert(self, value, explicit_type=True):
        try:
            return float(value)
        except ValueError:
            raise ValueError


@TypeConverter.register
class DecimalConverter(TypeConverter):
    type = Decimal

    def _convert(self, value, explicit_type=True):
        try:
            return Decimal(value)
        except InvalidOperation:
            # With Python 3 error messages by decimal module are not very
            # useful and cannot be included in our error messages:
            # https://bugs.python.org/issue26208
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
            value = value.encode('latin-1')
        except UnicodeEncodeError as err:
            raise ValueError("Character '%s' cannot be mapped to a byte."
                             % value[err.start:err.start+1])
        return value if not IRONPYTHON else bytes(value)


@TypeConverter.register
class ByteArrayConverter(TypeConverter):
    type = bytearray
    convert_none = False

    def _convert(self, value, explicit_type=True):
        try:
            return bytearray(value, 'latin-1')
        except UnicodeEncodeError as err:
            raise ValueError("Character '%s' cannot be mapped to a byte."
                             % value[err.start:err.start+1])


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
            raise ValueError("Value is datetime, not date.")
        return dt.date()


@TypeConverter.register
class TimeDeltaConverter(TypeConverter):
    type = timedelta

    def _convert(self, value, explicit_type=True):
        return convert_time(value, result_format='timedelta')


@TypeConverter.register
class EnumConverter(TypeConverter):
    type = Enum

    def __init__(self, enum=None):
        self._enum = enum

    @property
    def type_name(self):
        return self._enum.__name__ if self._enum else None

    def get_converter(self, type_):
        return EnumConverter(type_)

    def _convert(self, value, explicit_type=True):
        try:
            # This is compatible with the enum module in Python 3.4, its
            # enum34 backport, and the older enum module. `self._enum[value]`
            # wouldn't work with the old enum module.
            return getattr(self._enum, value)
        except AttributeError:
            members = self._get_members(self._enum)
            raise ValueError("%s does not have member '%s'. Available: %s"
                             % (self.type_name, value, seq2str(members)))

    def _get_members(self, enum):
        try:
            return list(enum.__members__)
        except AttributeError:    # old enum module
            return [attr for attr in dir(enum) if not attr.startswith('_')]


@TypeConverter.register
class NoneConverter(TypeConverter):
    type = type(None)

    def _convert(self, value, explicit_type=True):
        return value


@TypeConverter.register
class ListConverter(TypeConverter):
    type = list
    abc = abc.Sequence

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
    aliases = ('dict', 'map')

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

    def _convert(self, value, explicit_type=True):
        # There are issues w/ literal_eval. See self._literal_eval for details.
        if value == 'frozenset()' and not PY2:
            return frozenset()
        return frozenset(self._literal_eval(value, set))
