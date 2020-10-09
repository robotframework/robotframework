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

from java.lang import Byte, Short, Integer, Long, Boolean, Float, Double

from robot.variables import contains_variable
from robot.utils import is_string, is_list_like


class JavaArgumentCoercer(object):

    def __init__(self, signatures, argspec):
        self._argspec = argspec
        self._coercers = CoercerFinder().find_coercers(signatures)
        self._varargs_handler = VarargsHandler(argspec)

    def coerce(self, arguments, named, dryrun=False):
        arguments = self._varargs_handler.handle(arguments)
        arguments = [c.coerce(a, dryrun)
                     for c, a in zip(self._coercers, arguments)]
        if self._argspec.kwargs:
            arguments.append(dict(named))
        return arguments


class CoercerFinder(object):

    def find_coercers(self, signatures):
        return [self._get_coercer(types, position)
                for position, types in self._parse_types(signatures)]

    def _parse_types(self, signatures):
        types = {}
        for sig in signatures:
            for index, arg in enumerate(sig.args):
                types.setdefault(index + 1, []).append(arg)
        return sorted(types.items())

    def _get_coercer(self, types, position):
        possible = [BooleanCoercer(position), IntegerCoercer(position),
                    FloatCoercer(position), NullCoercer(position)]
        coercers = [self._get_coercer_for_type(t, possible) for t in types]
        if self._coercers_conflict(*coercers):
            return NullCoercer()
        return coercers[0]

    def _get_coercer_for_type(self, type, coercers):
        for coercer in coercers:
            if coercer.handles(type):
                return coercer

    def _coercers_conflict(self, first, *rest):
        return not all(coercer is first for coercer in rest)


class _Coercer(object):
    _name = ''
    _types = []
    _primitives = []

    def __init__(self, position=None):
        self._position = position

    def handles(self, type):
        return type in self._types or type.__name__ in self._primitives

    def coerce(self, argument, dryrun=False):
        if not is_string(argument) \
                or (dryrun and contains_variable(argument)):
            return argument
        try:
            return self._coerce(argument)
        except ValueError:
            raise ValueError('Argument at position %d cannot be coerced to %s.'
                             % (self._position, self._name))

    def _coerce(self, argument):
        raise NotImplementedError


class BooleanCoercer(_Coercer):
    _name = 'boolean'
    _types = [Boolean]
    _primitives = ['boolean']

    def _coerce(self, argument):
        try:
            return {'false': False, 'true': True}[argument.lower()]
        except KeyError:
            raise ValueError


class IntegerCoercer(_Coercer):
    _name = 'integer'
    _types = [Byte, Short, Integer, Long]
    _primitives = ['byte', 'short', 'int', 'long']

    def _coerce(self, argument):
        return int(argument)


class FloatCoercer(_Coercer):
    _name = 'floating point number'
    _types = [Float, Double]
    _primitives = ['float', 'double']

    def _coerce(self, argument):
        return float(argument)


class NullCoercer(_Coercer):

    def handles(self, argument):
        return True

    def _coerce(self, argument):
        return argument


class VarargsHandler(object):

    def __init__(self, argspec):
        self._index = argspec.minargs if argspec.varargs else -1

    def handle(self, arguments):
        if self._index > -1 and not self._passing_list(arguments):
            arguments[self._index:] = [arguments[self._index:]]
        return arguments

    def _passing_list(self, arguments):
        return self._correct_count(arguments) and is_list_like(arguments[-1])

    def _correct_count(self, arguments):
        return len(arguments) == self._index + 1
