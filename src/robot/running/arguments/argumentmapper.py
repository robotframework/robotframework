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

from robot.errors import DataError

if TYPE_CHECKING:
    from .argumentspec import ArgumentSpec


class ArgumentMapper:

    def __init__(self, arg_spec: 'ArgumentSpec'):
        self.arg_spec = arg_spec

    def map(self, positional, named, replace_defaults=True):
        template = KeywordCallTemplate(self.arg_spec)
        template.fill_positional(positional)
        template.fill_named(named)
        if replace_defaults:
            template.replace_defaults()
        return template.args, template.kwargs


class KeywordCallTemplate:

    def __init__(self, arg_spec: 'ArgumentSpec'):
        self.arg_spec = arg_spec
        self.args = [None if arg not in arg_spec.defaults
                     else DefaultValue(arg_spec.defaults[arg])
                     for arg in arg_spec.positional]
        self.kwargs = []

    def fill_positional(self, positional):
        self.args[:len(positional)] = positional

    def fill_named(self, named):
        spec = self.arg_spec
        for name, value in named:
            if name in spec.positional_or_named:
                index = spec.positional_or_named.index(name)
                self.args[index] = value
            elif spec.var_named or name in spec.named_only:
                self.kwargs.append((name, value))
            else:
                raise DataError(f"Non-existing named argument '{name}'.")
        named_names = {name for name, _ in named}
        for name in spec.named_only:
            if name not in named_names:
                value = DefaultValue(spec.defaults[name])
                self.kwargs.append((name, value))

    def replace_defaults(self):
        is_default = lambda arg: isinstance(arg, DefaultValue)
        while self.args and is_default(self.args[-1]):
            self.args.pop()
        self.args = [a if not is_default(a) else a.value for a in self.args]
        self.kwargs = [(n, v) for n, v in self.kwargs if not is_default(v)]


class DefaultValue:

    def __init__(self, value):
        self.value = value

    def resolve(self, variables):
        try:
            return variables.replace_scalar(self.value)
        except DataError as err:
            raise DataError(f'Resolving argument default values failed: {err}')
