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

from robot.utils import is_unicode
from robot.variables import contains_variable

from .typeconverters import TypeConverter


class ArgumentConverter(object):

    def __init__(self, argspec, dry_run=False):
        """:type argspec: :py:class:`robot.running.arguments.ArgumentSpec`"""
        self._argspec = argspec
        self._dry_run = dry_run

    def convert(self, positional, named):
        return self._convert_positional(positional), self._convert_named(named)

    def _convert_positional(self, positional):
        names = self._argspec.positional
        converted = [self._convert(name, value)
                     for name, value in zip(names, positional)]
        if self._argspec.varargs:
            converted.extend(self._convert(self._argspec.varargs, value)
                             for value in positional[len(names):])
        return converted

    def _convert_named(self, named):
        names = set(self._argspec.positional) | set(self._argspec.kwonlyargs)
        kwargs = self._argspec.kwargs
        return [(name, self._convert(name if name in names else kwargs, value))
                for name, value in named]

    def _convert(self, name, value):
        type_, explicit_type = self._get_type(name, value)
        if type_ is None or (self._dry_run and
                             contains_variable(value, identifiers='$@&%')):
            return value
        converter = TypeConverter.converter_for(type_)
        if converter is None:
            return value
        return converter.convert(name, value, explicit_type)

    def _get_type(self, name, value):
        if self._argspec.types is None or not is_unicode(value):
            return None, None
        if name in self._argspec.types:
            return self._argspec.types[name], True
        if name in self._argspec.defaults:
            return type(self._argspec.defaults[name]), False
        return None, None
