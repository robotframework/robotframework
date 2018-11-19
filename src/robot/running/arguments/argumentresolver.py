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
from robot.utils import is_string, is_dict_like, split_from_equals
from robot.variables import VariableSplitter

from .argumentvalidator import ArgumentValidator


class ArgumentResolver(object):

    def __init__(self, argspec, resolve_named=True,
                 resolve_variables_until=None, dict_to_kwargs=False):
        self._named_resolver = NamedArgumentResolver(argspec) \
            if resolve_named else NullNamedArgumentResolver()
        self._variable_replacer = VariableReplacer(resolve_variables_until)
        self._dict_to_kwargs = DictToKwargs(argspec, dict_to_kwargs)
        self._argument_validator = ArgumentValidator(argspec)

    def resolve(self, arguments, variables=None):
        positional, named = self._named_resolver.resolve(arguments, variables)
        positional, named = self._variable_replacer.replace(positional, named,
                                                            variables)
        positional, named = self._dict_to_kwargs.handle(positional, named)
        self._argument_validator.validate(positional, named,
                                          dryrun=variables is None)
        return positional, named


class NamedArgumentResolver(object):

    def __init__(self, argspec):
        self._argspec = argspec

    def resolve(self, arguments, variables=None):
        positional = []
        named = []
        for arg in arguments:
            if self._is_dict_var(arg):
                named.append(arg)
            elif self._is_named(arg, variables):
                named.append(split_from_equals(arg))
            elif named:
                self._raise_positional_after_named()
            else:
                positional.append(arg)
        return positional, named

    def _is_dict_var(self, arg):
        return (is_string(arg) and arg[:2] == '&{' and arg[-1] == '}' and
                VariableSplitter(arg).is_dict_variable())

    def _is_named(self, arg, variables=None):
        if not (is_string(arg) and '=' in arg):
            return False
        name, value = split_from_equals(arg)
        if value is None:
            return False
        if self._argspec.kwargs or self._argspec.kwonlyargs:
            return True
        if not self._argspec.supports_named:
            return False
        if variables:
            name = variables.replace_scalar(name)
        return name in self._argspec.positional

    def _raise_positional_after_named(self):
        raise DataError("%s '%s' got positional argument after named arguments."
                        % (self._argspec.type, self._argspec.name))


class NullNamedArgumentResolver(object):

    def resolve(self, arguments, variables=None):
        return arguments, {}


class DictToKwargs(object):

    def __init__(self, argspec, enabled=False):
        self._maxargs = argspec.maxargs
        self._enabled = enabled and bool(argspec.kwargs)

    def handle(self, positional, named):
        if self._enabled and self._extra_arg_has_kwargs(positional, named):
            named = positional.pop().items()
        return positional, named

    def _extra_arg_has_kwargs(self, positional, named):
        if named or len(positional) != self._maxargs + 1:
            return False
        return is_dict_like(positional[-1])


class VariableReplacer(object):

    def __init__(self, resolve_until=None):
        self._resolve_until = resolve_until

    def replace(self, positional, named, variables=None):
        # `variables` is None in dry-run mode and when using Libdoc.
        if variables:
            positional = variables.replace_list(positional, self._resolve_until)
            named = list(self._replace_named(named, variables.replace_scalar))
        else:
            positional = list(positional)
            named = [item for item in named if isinstance(item, tuple)]
        return positional, named

    def _replace_named(self, named, replace_scalar):
        for item in named:
            for name, value in self._get_replaced_named(item, replace_scalar):
                if not is_string(name):
                    raise DataError('Argument names must be strings.')
                yield name, value

    def _get_replaced_named(self, item, replace_scalar):
        if not isinstance(item, tuple):
            return replace_scalar(item).items()
        name, value = item
        return [(replace_scalar(name), replace_scalar(value))]
