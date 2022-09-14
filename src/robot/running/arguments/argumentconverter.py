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

from robot.variables import contains_variable

from .typeconverters import TypeConverter


class ArgumentConverter:

    def __init__(self, argspec, converters, dry_run=False, languages=None):
        """:type argspec: :py:class:`robot.running.arguments.ArgumentSpec`"""
        self._argspec = argspec
        self._converters = converters
        self._dry_run = dry_run
        self._languages = languages

    def convert(self, positional, named):
        return self._convert_positional(positional), self._convert_named(named)

    def _convert_positional(self, positional):
        names = self._argspec.positional
        converted = [self._convert(name, value)
                     for name, value in zip(names, positional)]
        if self._argspec.var_positional:
            converted.extend(self._convert(self._argspec.var_positional, value)
                             for value in positional[len(names):])
        return converted

    def _convert_named(self, named):
        names = set(self._argspec.positional) | set(self._argspec.named_only)
        var_named = self._argspec.var_named
        return [(name, self._convert(name if name in names else var_named, value))
                for name, value in named]

    def _convert(self, name, value):
        spec = self._argspec
        if (spec.types is None
                or self._dry_run and contains_variable(value, identifiers='$@&%')):
            return value
        conversion_error = None
        # Don't convert None if argument has None as a default value.
        # Python < 3.11 adds None to type hints automatically when using None as
        # a default value which preserves None automatically. This code keeps
        # the same behavior also with newer Python versions.
        if value is None and name in spec.defaults and spec.defaults[name] is None:
            return value
        if name in spec.types:
            converter = TypeConverter.converter_for(spec.types[name], self._converters,
                                                    self._languages)
            if converter:
                try:
                    return converter.convert(name, value)
                except ValueError as err:
                    conversion_error = err
        if name in spec.defaults:
            converter = TypeConverter.converter_for(type(spec.defaults[name]),
                                                    languages=self._languages)
            if converter:
                try:
                    return converter.convert(name, value, explicit_type=False,
                                             strict=bool(conversion_error))
                except ValueError as err:
                    conversion_error = conversion_error or err
        if conversion_error:
            raise conversion_error
        return value
