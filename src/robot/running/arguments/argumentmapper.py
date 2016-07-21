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

from robot.errors import DataError


class ArgumentMapper(object):

    def __init__(self, argspec):
        self._argspec = argspec

    def map(self, positional, named, replace_defaults=True):
        template = KeywordCallTemplate(self._argspec)
        template.fill_positional(positional)
        template.fill_named(named)
        if replace_defaults:
            template.replace_defaults()
        return template.args, template.kwargs


class KeywordCallTemplate(object):

    def __init__(self, argspec):
        self._positional = argspec.positional
        self._supports_kwargs = bool(argspec.kwargs)
        self._supports_named = argspec.supports_named
        self.args = [None] * argspec.minargs \
                    + [DefaultValue(d) for d in argspec.defaults]
        self.kwargs = []

    def fill_positional(self, positional):
        self.args[:len(positional)] = positional

    def fill_named(self, named):
        for name, value in named:
            if name in self._positional and self._supports_named:
                index = self._positional.index(name)
                self.args[index] = value
            elif self._supports_kwargs:
                self.kwargs.append((name, value))
            else:
                raise DataError("Non-existing named argument '%s'." % name)

    def replace_defaults(self):
        while self.args and isinstance(self.args[-1], DefaultValue):
            self.args.pop()
        self.args = [arg if not isinstance(arg, DefaultValue) else arg.value
                     for arg in self.args]


class DefaultValue(object):

    def __init__(self, value):
        self.value = value

    def resolve(self, variables):
        try:
            return variables.replace_scalar(self.value)
        except DataError as err:
            raise DataError('Resolving argument default values failed: %s'
                            % err.message)
