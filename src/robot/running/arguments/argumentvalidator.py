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
from robot.utils import plural_or_not as s, seq2str
from robot.variables import is_dict_variable, is_list_variable

if TYPE_CHECKING:
    from .argumentspec import ArgumentSpec


class ArgumentValidator:

    def __init__(self, arg_spec: 'ArgumentSpec'):
        self.spec = arg_spec

    def validate(self, positional, named, dryrun=False):
        named = set(name for name, value in named)
        if dryrun and (any(is_list_variable(arg) for arg in positional) or
                       any(is_dict_variable(arg) for arg in named)):
            return
        self._validate_no_multiple_values(positional, named, self.spec)
        self._validate_no_positional_only_as_named(named, self.spec)
        self._validate_positional_limits(positional, named, self.spec)
        self._validate_no_mandatory_missing(positional, named, self.spec)
        self._validate_no_named_only_missing(named, self.spec)
        self._validate_no_extra_named(named, self.spec)

    def _validate_no_multiple_values(self, positional, named, spec):
        for name in spec.positional[:len(positional)-len(spec.embedded)]:
            if name in named and name not in spec.positional_only:
                self._raise_error(f"got multiple values for argument '{name}'")

    def _raise_error(self, message):
        name = f"'{self.spec.name}' " if self.spec.name else ''
        raise DataError(f"{self.spec.type.capitalize()} {name}{message}.")

    def _validate_no_positional_only_as_named(self, named, spec):
        if not spec.var_named:
            for name in named:
                if name in spec.positional_only:
                    self._raise_error(f"does not accept argument '{name}' as named "
                                      f"argument")

    def _validate_positional_limits(self, positional, named, spec):
        count = len(positional) + self._named_positionals(named, spec)
        if not spec.minargs <= count <= spec.maxargs:
            self._raise_wrong_count(count, spec)

    def _named_positionals(self, named, spec):
        return sum(1 for n in named if n in spec.positional_or_named)

    def _raise_wrong_count(self, count, spec):
        embedded = len(spec.embedded)
        minargs = spec.minargs - embedded
        maxargs = spec.maxargs - embedded
        if minargs == maxargs:
            expected = f'{minargs} argument{s(minargs)}'
        elif not spec.var_positional:
            expected = f'{minargs} to {maxargs} arguments'
        else:
            expected = f'at least {minargs} argument{s(minargs)}'
        if spec.var_named or spec.named_only:
            expected = expected.replace('argument', 'non-named argument')
        self._raise_error(f"expected {expected}, got {count - embedded}")

    def _validate_no_mandatory_missing(self, positional, named, spec):
        for name in spec.positional[len(positional):]:
            if name not in spec.defaults and name not in named:
                self._raise_error(f"missing value for argument '{name}'")

    def _validate_no_named_only_missing(self, named, spec):
        defined = set(named) | set(spec.defaults)
        missing = [arg for arg in spec.named_only if arg not in defined]
        if missing:
            self._raise_error(f"missing named-only argument{s(missing)} "
                              f"{seq2str(sorted(missing))}")

    def _validate_no_extra_named(self, named, spec):
        if not spec.var_named:
            extra = set(named) - set(spec.positional_or_named) - set(spec.named_only)
            if extra:
                self._raise_error(f"got unexpected named argument{s(extra)} "
                                  f"{seq2str(sorted(extra))}")
