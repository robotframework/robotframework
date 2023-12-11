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

from abc import ABC, abstractmethod
from inspect import isclass, signature, Parameter
from typing import Any, Callable, get_type_hints

from robot.errors import DataError
from robot.utils import is_string, split_from_equals
from robot.variables import is_assign, is_scalar_assign

from .argumentspec import ArgumentSpec


class ArgumentParser(ABC):

    def __init__(self, type: str = 'Keyword',
                 error_reporter: 'Callable[[str], None] | None' = None):
        self.type = type
        self.error_reporter = error_reporter

    @abstractmethod
    def parse(self, source: Any, name: 'str|None' = None) -> ArgumentSpec:
        raise NotImplementedError

    def _report_error(self, error: str):
        if self.error_reporter:
            self.error_reporter(error)
        else:
            raise DataError(f'Invalid argument specification: {error}')


class PythonArgumentParser(ArgumentParser):

    def parse(self, method, name=None):
        try:
            sig = signature(method)
        except ValueError:        # Can occur with C functions (incl. many builtins).
            return ArgumentSpec(name, self.type, var_positional='args')
        except TypeError as err:  # Occurs if handler isn't actually callable.
            raise DataError(str(err))
        parameters = list(sig.parameters.values())
        # `inspect.signature` drops `self` with bound methods and that's the case when
        # inspecting keywords. `__init__` is got directly from class (i.e. isn't bound)
        # so we need to handle that case ourselves.
        # Partial objects do not have __name__ at least in Python =< 3.10.
        if getattr(method, '__name__', None) == '__init__':
            parameters = parameters[1:]
        spec = self._create_spec(parameters, name)
        self._set_types(spec, method)
        return spec

    def _create_spec(self, parameters, name):
        positional_only = []
        positional_or_named = []
        var_positional = None
        named_only = []
        var_named = None
        defaults = {}
        for param in parameters:
            kind = param.kind
            if kind == Parameter.POSITIONAL_ONLY:
                positional_only.append(param.name)
            elif kind == Parameter.POSITIONAL_OR_KEYWORD:
                positional_or_named.append(param.name)
            elif kind == Parameter.VAR_POSITIONAL:
                var_positional = param.name
            elif kind == Parameter.KEYWORD_ONLY:
                named_only.append(param.name)
            elif kind == Parameter.VAR_KEYWORD:
                var_named = param.name
            if param.default is not param.empty:
                defaults[param.name] = param.default
        return ArgumentSpec(name, self.type, positional_only, positional_or_named,
                            var_positional, named_only, var_named, defaults)

    def _set_types(self, spec, method):
        types = self._get_types(method)
        if isinstance(types, dict) and 'return' in types:
            spec.return_type = types.pop('return')
        spec.types = types

    def _get_types(self, method):
        # If types are set using the `@keyword` decorator, use them. Including when
        # types are explicitly disabled with `@keyword(types=None)`. Otherwise get
        # type hints.
        if isclass(method):
            method = method.__init__
        types = getattr(method, 'robot_types', ())
        if types or types is None:
            return types
        try:
            return get_type_hints(method)
        except Exception:  # Can raise pretty much anything
            # Not all functions have `__annotations__`.
            # https://github.com/robotframework/robotframework/issues/4059
            return getattr(method, '__annotations__', {})


class ArgumentSpecParser(ArgumentParser):

    def parse(self, arguments, name=None):
        positional_only = []
        positional_or_named = []
        var_positional = None
        named_only = []
        var_named = None
        defaults = {}
        named_only_separator_seen = positional_only_separator_seen = False
        target = positional_or_named
        for arg in arguments:
            arg = self._validate_arg(arg)
            if var_named:
                self._report_error('Only last argument can be kwargs.')
            elif self._is_positional_only_separator(arg):
                if positional_only_separator_seen:
                    self._report_error('Too many positional-only separators.')
                if named_only_separator_seen:
                    self._report_error('Positional-only separator must be before '
                                       'named-only arguments.')
                positional_only = positional_or_named
                target = positional_or_named = []
                positional_only_separator_seen = True
            elif isinstance(arg, tuple):
                arg, default = arg
                arg = self._format_arg(arg)
                target.append(arg)
                defaults[arg] = default
            elif self._is_var_named(arg):
                var_named = self._format_var_named(arg)
            elif self._is_var_positional(arg):
                if named_only_separator_seen:
                    self._report_error('Cannot have multiple varargs.')
                if not self._is_named_only_separator(arg):
                    var_positional = self._format_var_positional(arg)
                named_only_separator_seen = True
                target = named_only
            elif defaults and not named_only_separator_seen:
                self._report_error('Non-default argument after default arguments.')
            else:
                arg = self._format_arg(arg)
                target.append(arg)
        return ArgumentSpec(name, self.type, positional_only, positional_or_named,
                            var_positional, named_only, var_named, defaults)

    @abstractmethod
    def _validate_arg(self, arg):
        raise NotImplementedError

    @abstractmethod
    def _is_var_named(self, arg):
        raise NotImplementedError

    @abstractmethod
    def _format_var_named(self, kwargs):
        raise NotImplementedError

    @abstractmethod
    def _is_positional_only_separator(self, arg):
        raise NotImplementedError

    @abstractmethod
    def _is_named_only_separator(self, arg):
        raise NotImplementedError

    @abstractmethod
    def _is_var_positional(self, arg):
        raise NotImplementedError

    @abstractmethod
    def _format_var_positional(self, varargs):
        raise NotImplementedError

    def _format_arg(self, arg):
        return arg

    def _add_arg(self, spec, arg, named_only=False):
        arg = self._format_arg(arg)
        target = spec.positional_or_named if not named_only else spec.named_only
        target.append(arg)
        return arg


class DynamicArgumentParser(ArgumentSpecParser):

    def _validate_arg(self, arg):
        if isinstance(arg, tuple):
            if self._is_invalid_tuple(arg):
                self._report_error(f'Invalid argument "{arg}".')
            if len(arg) == 1:
                return arg[0]
            return arg
        if '=' in arg:
            return tuple(arg.split('=', 1))
        return arg

    def _is_invalid_tuple(self, arg):
        return (len(arg) > 2
                or not is_string(arg[0])
                or (arg[0].startswith('*') and len(arg) > 1))

    def _is_var_named(self, arg):
        return arg[:2] == '**'

    def _format_var_named(self, kwargs):
        return kwargs[2:]

    def _is_var_positional(self, arg):
        return arg and arg[0] == '*'

    def _is_positional_only_separator(self, arg):
        return arg == '/'

    def _is_named_only_separator(self, arg):
        return arg == '*'

    def _format_var_positional(self, varargs):
        return varargs[1:]


class UserKeywordArgumentParser(ArgumentSpecParser):

    def _validate_arg(self, arg):
        arg, default = split_from_equals(arg)
        if not (is_assign(arg) or arg == '@{}'):
            self._report_error(f"Invalid argument syntax '{arg}'.")
        if default is None:
            return arg
        if not is_scalar_assign(arg):
            typ = 'list' if arg[0] == '@' else 'dictionary'
            self._report_error(f"Only normal arguments accept default values, "
                               f"{typ} arguments like '{arg}' do not.")
        return arg, default

    def _is_var_named(self, arg):
        return arg and arg[0] == '&'

    def _format_var_named(self, kwargs):
        return kwargs[2:-1]

    def _is_var_positional(self, arg):
        return arg and arg[0] == '@'

    def _is_positional_only_separator(self, arg):
        return False

    def _is_named_only_separator(self, arg):
        return arg == '@{}'

    def _format_var_positional(self, varargs):
        return varargs[2:-1]

    def _format_arg(self, arg):
        return arg[2:-1]
