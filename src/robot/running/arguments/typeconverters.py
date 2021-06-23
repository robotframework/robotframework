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
try:
    from typing import Union
except ImportError:
    class Union(object):
        pass
from datetime import datetime, date, timedelta
from decimal import InvalidOperation, Decimal
try:
    from enum import Enum
except ImportError:    # Standard in Py 3.4+ but can be separately installed
    class Enum(object):
        pass
from numbers import Integral, Real

from robot.libraries.DateTime import convert_date, convert_time
from robot.utils import (FALSE_STRINGS, IRONPYTHON, TRUE_STRINGS, PY_VERSION, PY2,
                         eq, get_error_message, seq2str, type_name, typeddict_types,
                         unic, unicode)


class TypeConverter(object):
    type = None
    type_name = None
    abc = None
    aliases = ()
    value_types = (unicode,)
    _converters = OrderedDict()
    _type_aliases = {}

    def __init__(self, used_type):
        self.used_type = used_type

    @classmethod
    def register(cls, converter):
        cls._converters[converter.type] = converter
        for name in (converter.type_name,) + converter.aliases:
            if name is not None and not isinstance(name, property):
                cls._type_aliases[name.lower()] = converter.type
        return converter

    @classmethod
    def converter_for(cls, type_):
        if getattr(type_, '__origin__', None) and type_.__origin__ is not Union:
            type_ = type_.__origin__
        if isinstance(type_, (str, unicode)):
            try:
                type_ = cls._type_aliases[type_.lower()]
            except KeyError:
                return None
        if type_ in cls._converters:
            return cls._converters[type_](type_)
        for converter in cls._converters.values():
            if converter.handles(type_):
                return converter(type_)
        return None

    @classmethod
    def handles(cls, type_):
        handled = (cls.type, cls.abc) if cls.abc else cls.type
        return isinstance(type_, type) and issubclass(type_, handled)

    def convert(self, name, value, explicit_type=True, strict=True):
        if self.no_conversion_needed(value):
            return value
        if not self._handles_value(value):
            return self._handle_error(name, value, strict=strict)
        try:
            if not isinstance(value, unicode):
                return self._non_string_convert(value, explicit_type)
            return self._convert(value, explicit_type)
        except ValueError as error:
            return self._handle_error(name, value, error, strict)

    def no_conversion_needed(self, value):
        try:
            return isinstance(value, self.used_type)
        except TypeError:
            # If the used type doesn't like `isinstance` (e.g. TypedDict),
            # compare the value to the generic type instead.
            if self.type and self.type is not self.used_type:
                return isinstance(value, self.type)
            raise

    def _handles_value(self, value):
        return isinstance(value, self.value_types)

    def _non_string_convert(self, value, explicit_type=True):
        return self._convert(value, explicit_type)

    def _convert(self, value, explicit_type=True):
        raise NotImplementedError

    def _handle_error(self, name, value, error=None, strict=True):
        if not strict:
            return value
        value_type = '' if isinstance(value, unicode) else ' (%s)' % type_name(value)
        ending = u': %s' % error if (error and error.args) else '.'
        raise ValueError(
            "Argument '%s' got value '%s'%s that cannot be converted to %s%s"
            % (name, unic(value), value_type, self.type_name, ending)
        )

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
class StringConverter(TypeConverter):
    type = unicode
    type_name = 'string'
    aliases = ('string', 'str', 'unicode')

    def _handles_value(self, value):
        return True

    def _convert(self, value, explicit_type=True):
        if not explicit_type:
            return value
        try:
            return unicode(value)
        except Exception:
            raise ValueError(get_error_message())


@TypeConverter.register
class BooleanConverter(TypeConverter):
    value_types = (unicode, int, float, type(None))
    type = bool
    type_name = 'boolean'
    aliases = ('bool',)

    def _non_string_convert(self, value, explicit_type=True):
        return value

    def _convert(self, value, explicit_type=True):
        upper = value.upper()
        if upper == 'NONE':
            return None
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
    value_types = (unicode, float)

    def _non_string_convert(self, value, explicit_type=True):
        if value.is_integer():
            return int(value)
        raise ValueError('Conversion would lose precision.')

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
    type_name = 'float'
    aliases = ('double',)
    value_types = (unicode, Real)

    def _convert(self, value, explicit_type=True):
        try:
            return float(value)
        except ValueError:
            raise ValueError


@TypeConverter.register
class DecimalConverter(TypeConverter):
    type = Decimal
    type_name = 'decimal'
    value_types = (unicode, int, float)

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
    type_name = 'bytes'
    value_types = (unicode, bytearray)

    def _non_string_convert(self, value, explicit_type=True):
        return bytes(value)

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
    type_name = 'bytearray'
    value_types = (unicode, bytes)

    def _non_string_convert(self, value, explicit_type=True):
        return bytearray(value)

    def _convert(self, value, explicit_type=True):
        try:
            return bytearray(value, 'latin-1')
        except UnicodeEncodeError as err:
            raise ValueError("Character '%s' cannot be mapped to a byte."
                             % value[err.start:err.start+1])


@TypeConverter.register
class DateTimeConverter(TypeConverter):
    type = datetime
    type_name = 'datetime'
    value_types = (unicode, int, float)

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
    value_types = (unicode, int, float)

    def _convert(self, value, explicit_type=True):
        return convert_time(value, result_format='timedelta')


@TypeConverter.register
class EnumConverter(TypeConverter):
    type = Enum

    @property
    def type_name(self):
        return self.used_type.__name__

    def _convert(self, value, explicit_type=True):
        enum = self.used_type
        try:
            # This is compatible with the enum module in Python 3.4, its
            # enum34 backport, and the older enum module. `enum[value]`
            # wouldn't work with the old enum module.
            return getattr(enum, value)
        except AttributeError:
            members = sorted(self._get_members(enum))
            matches = [m for m in members if eq(m, value, ignore='_')]
            if not matches:
                raise ValueError("%s does not have member '%s'. Available: %s"
                                 % (self.type_name, value, seq2str(members)))
            if len(matches) > 1:
                raise ValueError("%s has multiple members matching '%s'. Available: %s"
                                 % (self.type_name, value, seq2str(matches)))
            return getattr(enum, matches[0])

    def _get_members(self, enum):
        try:
            return list(enum.__members__)
        except AttributeError:    # old enum module
            return [attr for attr in dir(enum) if not attr.startswith('_')]


@TypeConverter.register
class NoneConverter(TypeConverter):
    type = type(None)
    type_name = 'None'

    def __init__(self, used_type):
        if used_type is None:
            used_type = type(None)
        TypeConverter.__init__(self, used_type)

    @classmethod
    def handles(cls, type_):
        return type_ in (type(None), None)

    def _convert(self, value, explicit_type=True):
        if value.upper() == 'NONE':
            return None
        raise ValueError


@TypeConverter.register
class ListConverter(TypeConverter):
    type = list
    type_name = 'list'
    abc = abc.Sequence
    value_types = (unicode, tuple)

    def no_conversion_needed(self, value):
        if isinstance(value, (str, unicode)):
            return False
        return TypeConverter.no_conversion_needed(self, value)

    def _non_string_convert(self, value, explicit_type=True):
        return list(value)

    def _convert(self, value, explicit_type=True):
        return self._literal_eval(value, list)


@TypeConverter.register
class TupleConverter(TypeConverter):
    type = tuple
    type_name = 'tuple'
    value_types = (unicode, list)

    def _non_string_convert(self, value, explicit_type=True):
        return tuple(value)

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
    type_name = 'set'
    value_types = (unicode, frozenset, list, tuple, abc.Mapping)
    abc = abc.Set

    def _non_string_convert(self, value, explicit_type=True):
        return set(value)

    def _convert(self, value, explicit_type=True):
        return self._literal_eval(value, set)


@TypeConverter.register
class FrozenSetConverter(TypeConverter):
    type = frozenset
    type_name = 'frozenset'
    value_types = (unicode, set, list, tuple, abc.Mapping)

    def _non_string_convert(self, value, explicit_type=True):
        return frozenset(value)

    def _convert(self, value, explicit_type=True):
        # There are issues w/ literal_eval. See self._literal_eval for details.
        if value == 'frozenset()' and not PY2:
            return frozenset()
        return frozenset(self._literal_eval(value, set))


@TypeConverter.register
class CombinedConverter(TypeConverter):
    type = Union

    def __init__(self, union):
        self.types = self._none_to_nonetype(self._get_types(union))
        self.converters = [TypeConverter.converter_for(t) for t in self.types]

    def _get_types(self, union):
        if not union:
            return ()
        if isinstance(union, tuple):
            return union
        try:
            return union.__args__
        except AttributeError:
            # Python 3.5.2's typing uses __union_params__ instead
            # of __args__. This block can likely be safely removed
            # when Python 3.5 support is dropped
            return union.__union_params__

    def _none_to_nonetype(self, types):
        return tuple(t if t is not None else type(None) for t in types)

    @property
    def type_name(self):
        return ' or '.join(type_name(t) for t in self.types) if self.types else None

    @classmethod
    def handles(cls, type_):
        return getattr(type_, '__origin__', None) is Union or isinstance(type_, tuple)

    def _handles_value(self, value):
        return True

    def no_conversion_needed(self, value):
        for converter in self.converters:
            if converter and converter.no_conversion_needed(value):
                return True
        return False

    def _convert(self, value, explicit_type=True):
        for converter in self.converters:
            if not converter:
                return value
            try:
                return converter.convert('', value, explicit_type)
            except ValueError:
                pass
        raise ValueError
