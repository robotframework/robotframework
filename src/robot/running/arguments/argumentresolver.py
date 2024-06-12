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
from robot.utils import is_dict_like, split_from_equals
from robot.variables import is_dict_variable

from .argumentvalidator import ArgumentValidator
from ..model import Argument

if TYPE_CHECKING:
    from .argumentspec import ArgumentSpec


class ArgumentResolver:

    def __init__(self, spec: 'ArgumentSpec',
                 resolve_named: bool = True,
                 resolve_args_until: 'int|None' = None,
                 dict_to_kwargs: bool = False):
        self.named_resolver = NamedArgumentResolver(spec) \
              if resolve_named else NullNamedArgumentResolver()
        self.variable_replacer = VariableReplacer(spec, resolve_args_until)
        self.dict_to_kwargs = DictToKwargs(spec, dict_to_kwargs)
        self.argument_validator = ArgumentValidator(spec)

    def resolve(self, arguments, variables=None):
        positional, named = self.named_resolver.resolve(arguments, variables)
        positional, named = self.variable_replacer.replace(positional, named, variables)
        positional, named = self.dict_to_kwargs.handle(positional, named)
        self.argument_validator.validate(positional, named, dryrun=variables is None)
        return positional, named


class NamedArgumentResolver:

    def __init__(self, spec: 'ArgumentSpec'):
        self.spec = spec

    def resolve(self, arguments, variables=None):
        spec = self.spec
        positional = list(arguments[:len(spec.embedded)])
        named = []
        for arg in arguments[len(spec.embedded):]:
            if is_dict_variable(arg):
                named.append(arg)
            else:
                name, value = self._split_named(arg, named, variables, spec)
                if name is not None:
                    named.append((name, value))
                elif named:
                    self._raise_positional_after_named()
                else:
                    positional.append(value)
        return positional, named

    def _split_named(self, arg, previous_named, variables, spec):
        if isinstance(arg, Argument):
            return arg.name, arg.value
        name, value = split_from_equals(arg)
        if value is None or not self._is_named(name, previous_named, variables, spec):
            return None, arg
        return name, value

    def _is_named(self, name, previous_named, variables, spec):
        if previous_named or spec.var_named:
            return True
        if variables:
            try:
                name = variables.replace_scalar(name)
            except DataError:
                return False
        return name in spec.named

    def _raise_positional_after_named(self):
        raise DataError(f"{self.spec.type.capitalize()} '{self.spec.name}' "
                        f"got positional argument after named arguments.")


class NullNamedArgumentResolver:

    def resolve(self, arguments, variables=None):
        return arguments, []


class DictToKwargs:

    def __init__(self, spec: 'ArgumentSpec', enabled: bool = False):
        self.maxargs = spec.maxargs
        self.enabled = enabled and bool(spec.var_named)

    def handle(self, positional, named):
        if self.enabled and self._extra_arg_has_kwargs(positional, named):
            named = positional.pop().items()
        return positional, named

    def _extra_arg_has_kwargs(self, positional, named):
        if named or len(positional) != self.maxargs + 1:
            return False
        return is_dict_like(positional[-1])


class VariableReplacer:

    def __init__(self, spec: 'ArgumentSpec', resolve_until: 'int|None' = None):
        self.spec = spec
        self.resolve_until = resolve_until

    def replace(self, positional, named, variables=None):
        # `variables` is None in dry-run mode and when using Libdoc.
        if variables:
            if self.spec.embedded:
                embedded = len(self.spec.embedded)
                positional = [
                    variables.replace_scalar(emb) for emb in positional[:embedded]
                ] + variables.replace_list(positional[embedded:])
            else:
                positional = variables.replace_list(positional, self.resolve_until)
            named = list(self._replace_named(named, variables.replace_scalar))
        else:
            # If `var` isn't a tuple, it's a &{dict} variables.
            named = [var if isinstance(var, tuple) else (var, var) for var in named]
        return positional, named

    def _replace_named(self, named, replace_scalar):
        for item in named:
            for name, value in self._get_replaced_named(item, replace_scalar):
                if not isinstance(name, str):
                    raise DataError('Argument names must be strings.')
                yield name, value

    def _get_replaced_named(self, item, replace_scalar):
        if not isinstance(item, tuple):
            return replace_scalar(item).items()
        name, value = item
        return [(replace_scalar(name), replace_scalar(value))]
