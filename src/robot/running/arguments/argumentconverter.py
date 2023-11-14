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

from typing import TYPE_CHECKING

from robot.variables import contains_variable

from .typeinfo import TypeInfo

if TYPE_CHECKING:
    from robot.conf import LanguagesLike

    from .argumentspec import ArgumentSpec
    from .customconverters import CustomArgumentConverters


class ArgumentConverter:

    def __init__(self, arg_spec: 'ArgumentSpec',
                 custom_converters: 'CustomArgumentConverters',
                 dry_run: bool = False,
                 languages: 'LanguagesLike' = None):
        self.spec = arg_spec
        self.custom_converters = custom_converters
        self.dry_run = dry_run
        self.languages = languages

    def convert(self, positional, named):
        return self._convert_positional(positional), self._convert_named(named)

    def _convert_positional(self, positional):
        names = self.spec.positional
        converted = [self._convert(name, value)
                     for name, value in zip(names, positional)]
        if self.spec.var_positional:
            converted.extend(self._convert(self.spec.var_positional, value)
                             for value in positional[len(names):])
        return converted

    def _convert_named(self, named):
        names = set(self.spec.positional) | set(self.spec.named_only)
        var_named = self.spec.var_named
        return [(name, self._convert(name if name in names else var_named, value))
                for name, value in named]

    def _convert(self, name, value):
        spec = self.spec
        if (spec.types is None
                or self.dry_run and contains_variable(value, identifiers='$@&%')):
            return value
        conversion_error = None
        # Don't convert None if argument has None as a default value.
        # Python < 3.11 adds None to type hints automatically when using None as
        # a default value which preserves None automatically. This code keeps
        # the same behavior also with newer Python versions. We can consider
        # changing this once Python 3.11 is our minimum supported version.
        if value is None and name in spec.defaults and spec.defaults[name] is None:
            return value
        # Primarily convert arguments based on type hints.
        if name in spec.types:
            info: TypeInfo = spec.types[name]
            try:
                return info.convert(value, name, self.custom_converters, self.languages)
            except ValueError as err:
                conversion_error = err
            except TypeError:
                pass
        # Try conversion also based on the default value type. We probably should
        # do this only if there is no explicit type hint, but Python < 3.11
        # handling `arg: type = None` differently than newer versions would mean
        # that conversion behavior depends on the Python version. Once Python 3.11
        # is our minimum supported version, we can consider reopening
        # https://github.com/robotframework/robotframework/issues/4881
        if name in spec.defaults:
            typ = type(spec.defaults[name])
            if typ == str:      # Don't convert arguments to strings.
                info = TypeInfo()
            elif typ == int:    # Try also conversion to float.
                info = TypeInfo.from_sequence([int, float])
            else:
                info = TypeInfo.from_type(typ)
            try:
                return info.convert(value, name, languages=self.languages)
            except (ValueError, TypeError):
                pass
        if conversion_error:
            raise conversion_error
        return value
