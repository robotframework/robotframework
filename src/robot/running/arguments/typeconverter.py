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
    unicode = str
except ImportError:    # Python 2
    import collections as abc
from datetime import datetime, date, timedelta
from decimal import InvalidOperation, Decimal
try:
    from enum import EnumMeta
except ImportError:    # Standard in Py 3.4+ but can be separately installed
    class EnumMeta(object):
        pass

from robot.libraries.DateTime import convert_date, convert_time
from robot.utils import FALSE_STRINGS, TRUE_STRINGS, PY2, is_unicode


class TypeConverter(object):

    def __init__(self, argspec):
        self._argspec = argspec
        self._converters = OrderedDict([
            (dict, self._convert_dict),
            (set, self._convert_set),
            (frozenset, self._convert_frozenset),
            (list, self._convert_list),
            (tuple, self._convert_tuple),
            (abc.Mapping, self._convert_mapping),
            (abc.Set, self._convert_set),
            (abc.Iterable, self._convert_iterable),
            (bool, self._convert_bool),
            (int, self._convert_int),
            (float, self._convert_float),
            (Decimal, self._convert_decimal),
            (bytes, self._convert_bytes),
            (bytearray, self._convert_bytearray),
            (datetime, self._convert_datetime),
            (date, self._convert_date),
            (timedelta, self._convert_timedelta),
            (type(None), self._convert_none)
        ])

    def convert(self, positional, named):
        names = self._argspec.positional
        positional, varargs = positional[:len(names)], positional[len(names):]
        positional = [self._convert(name, value)
                      for name, value in zip(names, positional)]
        named = [(name, self._convert(name, value)) for name, value in named]
        return positional + varargs, named

    def _convert(self, name, value):
        if not is_unicode(value):
            return value
        if name in self._argspec.annotations:
            type_ = self._argspec.annotations[name]
            explicit_type = True
        elif name in self._argspec.default_values:
            type_ = type(self._argspec.default_values[name])
            explicit_type = False
        else:
            return value
        converter = self._get_converter(type_)
        if not converter:
            return value
        # TODO: Clean this up. Most likely converters should be classes.
        # Also, consider allowing 'NONE' with enums.
        if value.upper() == 'NONE' and converter not in (self._convert_bytes,
                                                         self._convert_bytearray):
            return None
        return converter(name, value, explicit_type)

    def _get_converter(self, type_):
        if issubclass(type_, (str, unicode)) or not isinstance(type_, type):
            return None
        if type_ in self._converters:
            return self._converters[type_]
        if isinstance(type_, EnumMeta):
            return self._get_enum_converter(type_)
        for converter_type in self._converters:
            if issubclass(type_, converter_type):
                return self._converters[converter_type]
        return None

    def _get_enum_converter(self, enum_):
        def _convert_enum(name, value, explicit_type=True):
            try:
                return enum_[value]
            except KeyError:
                return self._handle_error(name, value, enum_.__name__,
                                          explicit_type)
        return _convert_enum

    def _convert_int(self, name, value, explicit_type=True):
        try:
            return int(value)
        except ValueError:
            pass
        try:
            if not explicit_type:
                return float(value)
        except ValueError:
            pass
        return self._handle_error(name, value, 'integer', explicit_type)

    def _convert_float(self, name, value, explicit_type=True):
        try:
            return float(value)
        except ValueError:
            return self._handle_error(name, value, 'float', explicit_type)

    def _convert_decimal(self, name, value, explicit_type=True):
        try:
            return Decimal(value)
        except InvalidOperation:
            return self._handle_error(name, value, 'decimal', explicit_type)

    def _convert_bool(self, name, value, explicit_type=True):
        upper = value.upper()
        if upper in TRUE_STRINGS:
            return True
        if upper in FALSE_STRINGS:
            return False
        return value

    def _convert_list(self, name, value, explicit_type=True):
        return self._literal_eval(name, value, list, explicit_type)

    def _convert_tuple(self, name, value, explicit_type=True):
        return self._literal_eval(name, value, tuple, explicit_type)

    def _convert_dict(self, name, value, explicit_type=True,
                      type_name='dictionary'):
        return self._literal_eval(name, value, dict, explicit_type, type_name)

    def _convert_set(self, name, value, explicit_type=True):
        if PY2:    # ast.literal_eval() doesn't support sets in Python 2
            return value
        if value == 'set()':
            return set()
        return self._literal_eval(name, value, set, explicit_type)

    def _convert_frozenset(self, name, value, explicit_type=True):
        if PY2:    # ast.literal_eval() doesn't support sets in Python 2
            return value
        if value == 'frozenset()':
            return frozenset()
        value = self._convert_set(name, value, explicit_type)
        return frozenset(value) if isinstance(value, set) else value

    def _convert_iterable(self, name, value, explicit_type=True):
        for converter in (self._convert_list, self._convert_tuple,
                          self._convert_set, self._convert_dict):
            try:
                return converter(name, value, explicit_type=True)
            except ValueError:
                pass
        return self._handle_error(name, value, 'iterable', explicit_type)

    def _convert_mapping(self, name, value, explicit_type=True):
        return self._convert_dict(name, value, explicit_type, 'mapping')

    def _convert_bytes(self, name, value, explicit_type=True):
        try:
            return value.encode('latin-1')
        except UnicodeEncodeError:
            return self._handle_error(name, value, 'bytes', explicit_type)

    def _convert_bytearray(self, name, value, explicit_type=True):
        try:
            return bytearray(value, 'latin-1')
        except UnicodeEncodeError:
            return self._handle_error(name, value, 'bytearray', explicit_type)

    def _convert_datetime(self, name, value, explicit_type=True):
        try:
            return convert_date(value, result_format='datetime')
        except ValueError:
            return self._handle_error(name, value, 'datetime', explicit_type)

    def _convert_date(self, name, value, explicit_type=True):
        try:
            dt = convert_date(value, result_format='datetime')
            if dt.hour or dt.minute or dt.second or dt.microsecond:
                raise ValueError
            return dt.date()
        except ValueError:
            return self._handle_error(name, value, 'date', explicit_type)

    def _convert_timedelta(self, name, value, explicit_type=True):
        try:
            return convert_time(value, result_format='timedelta')
        except ValueError:
            return self._handle_error(name, value, 'timedelta', explicit_type)

    def _convert_none(self, name, value, explicit_type=True):
        return value

    def _literal_eval(self, name, value, expected, explicit_type=True,
                      expected_name=None):
        if not expected_name:
            expected_name = expected.__name__
        try:
            value = literal_eval(value)
            if not isinstance(value, expected):
                raise TypeError
            return value
        except (ValueError, SyntaxError, TypeError):
            return self._handle_error(name, value, expected_name, explicit_type)

    def _handle_error(self, name, value, expected, explicit_type=True):
        if explicit_type:
            raise ValueError("Argument '%s' cannot be converted to %s, "
                             "got '%s'." % (name, expected, value))
        return value
