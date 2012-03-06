#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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
from java.lang import Byte, Short, Integer, Long, Boolean, Float, Double


class ArgumentCoercer:

    def __init__(self, signatures):
        types = self._parse_types(signatures)
        self._coercers = [_CoercionFunction(t, i+1) for i, t in types]

    def _parse_types(self, signatures):
        types = {}
        for sig in signatures:
            for index, arg in enumerate(sig.args):
                types.setdefault(index, []).append(arg)
        return sorted(types.items())

    def __call__(self, args):
        return [coercer(arg) for coercer, arg in zip(self._coercers, args)]


class _CoercionFunction:
    _bool_types = [Boolean]
    _int_types = [Byte, Short, Integer, Long]
    _float_types = [Float, Double]
    _bool_primitives = ['boolean']
    _int_primitives = ['byte', 'short', 'int', 'long']
    _float_primitives = ['float', 'double']
    _bool_primitives = ["<type 'boolean'>"]
    _int_primitives = ["<type '%s'>" % p for p in _int_primitives]
    _float_primitives = ["<type '%s'>" % p for p in _float_primitives]

    def __init__(self, arg_types, position):
        self._position = position
        self.__coercer = None
        for arg in arg_types:
            if not (self._set_bool(arg) or
                    self._set_int(arg) or
                    self._set_float(arg)):
                self.__coercer = self._no_coercion

    def __call__(self, arg):
        if not isinstance(arg, basestring):
            return arg
        return self.__coercer(arg)

    def _set_bool(self, arg):
        return self._set_coercer(arg, self._bool_types,
                                 self._bool_primitives, self._to_bool)

    def _set_int(self, arg):
        return self._set_coercer(arg, self._int_types,
                                 self._int_primitives, self._to_int)

    def _set_float(self, arg):
        return self._set_coercer(arg, self._float_types,
                                 self._float_primitives, self._to_float)

    def _set_coercer(self, arg, type_list, primitive_list, coercer):
        if arg in type_list or str(arg) in primitive_list:
            if self.__coercer is None:
                self.__coercer = coercer
            elif self.__coercer != coercer:
                self.__coercer = self._no_coercion
            return True
        return False

    def _to_bool(self, arg):
        try:
            return {'false': False, 'true': True}[arg.lower()]
        except KeyError:
            self._coercion_failed('boolean')

    def _to_int(self, arg):
        try:
            return int(arg)
        except ValueError:
            self._coercion_failed('integer')

    def _to_float(self, arg):
        try:
            return float(arg)
        except ValueError:
            self._coercion_failed('floating point number')

    def _no_coercion(self, arg):
        return arg

    def _coercion_failed(self, arg_type):
        raise ValueError('Argument at position %d cannot be coerced to %s'
                         % (self._position, arg_type))
