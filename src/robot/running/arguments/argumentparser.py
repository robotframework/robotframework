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

from inspect import isclass, signature, Parameter
from typing import get_type_hints

from robot.errors import DataError
from robot.utils import is_string, split_from_equals
from robot.variables import is_assign, is_scalar_assign

from .argumentspec import ArgumentSpec


class _ArgumentParser:

    def __init__(self, type='Keyword', error_reporter=None):
        self._type = type
        self._error_reporter = error_reporter

    def parse(self, source, name=None):
        raise NotImplementedError

    def _report_error(self, error):
        if self._error_reporter:
            self._error_reporter(error)
        else:
            raise DataError('Invalid argument specification: %s' % error)


class PythonArgumentParser(_ArgumentParser):

    def parse(self, handler, name=None):
        spec = ArgumentSpec(name, self._type)
        self._set_args(spec, handler)
        self._set_types(spec, handler)
        return spec

    def _set_args(self, spec, handler):
        try:
            sig = signature(handler)
        except ValueError:  # Can occur w/ C functions (incl. many builtins).
            spec.var_positional = 'args'
            return
        parameters = list(sig.parameters.values())
        # `inspect.signature` drops `self` with bound methods and that's the case when
        # inspecting keywords. `__init__` is got directly from class (i.e. isn't bound)
        # so we need to handle that case ourselves.
        if handler.__name__ == '__init__':
            parameters = parameters[1:]
        setters = {
            Parameter.POSITIONAL_ONLY: spec.positional_only.append,
            Parameter.POSITIONAL_OR_KEYWORD: spec.positional_or_named.append,
            Parameter.VAR_POSITIONAL: lambda name: setattr(spec, 'var_positional', name),
            Parameter.KEYWORD_ONLY: spec.named_only.append,
            Parameter.VAR_KEYWORD: lambda name: setattr(spec, 'var_named', name),
        }
        for param in parameters:
            setters[param.kind](param.name)
            if param.default is not param.empty:
                spec.defaults[param.name] = param.default

    def _set_types(self, spec, handler):
        # If types are set using the `@keyword` decorator, use them. Including when
        # types are explicitly disabled with `@keyword(types=None)`. Otherwise read
        # type hints.
        if isclass(handler):
            handler = handler.__init__
        robot_types = getattr(handler, 'robot_types', ())
        if robot_types or robot_types is None:
            spec.types = robot_types
        else:
            spec.types = self._get_type_hints(handler)

    def _get_type_hints(self, handler):
        try:
            return get_type_hints(handler)
        except Exception:  # Can raise pretty much anything
            # Not all functions have `__annotations__`.
            # https://github.com/robotframework/robotframework/issues/4059
            return getattr(handler, '__annotations__', {})


class _ArgumentSpecParser(_ArgumentParser):

    def parse(self, argspec, name=None):
        spec = ArgumentSpec(name, self._type)
        named_only = False
        for arg in argspec:
            arg = self._validate_arg(arg)
            if spec.var_named:
                self._report_error('Only last argument can be kwargs.')
            elif isinstance(arg, tuple):
                arg, default = arg
                arg = self._add_arg(spec, arg, named_only)
                spec.defaults[arg] = default
            elif self._is_kwargs(arg):
                spec.var_named = self._format_kwargs(arg)
            elif self._is_varargs(arg):
                if named_only:
                    self._report_error('Cannot have multiple varargs.')
                if not self._is_kw_only_separator(arg):
                    spec.var_positional = self._format_varargs(arg)
                named_only = True
            elif spec.defaults and not named_only:
                self._report_error('Non-default argument after default arguments.')
            else:
                self._add_arg(spec, arg, named_only)
        return spec

    def _validate_arg(self, arg):
        raise NotImplementedError

    def _is_kwargs(self, arg):
        raise NotImplementedError

    def _format_kwargs(self, kwargs):
        raise NotImplementedError

    def _is_kw_only_separator(self, arg):
        raise NotImplementedError

    def _is_varargs(self, arg):
        raise NotImplementedError

    def _format_varargs(self, varargs):
        raise NotImplementedError

    def _format_arg(self, arg):
        return arg

    def _add_arg(self, spec, arg, named_only=False):
        arg = self._format_arg(arg)
        target = spec.positional_or_named if not named_only else spec.named_only
        target.append(arg)
        return arg


class DynamicArgumentParser(_ArgumentSpecParser):

    def _validate_arg(self, arg):
        if isinstance(arg, tuple):
            if self._is_invalid_tuple(arg):
                self._report_error('Invalid argument "%s".' % (arg,))
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

    def _is_kwargs(self, arg):
        return arg.startswith('**')

    def _format_kwargs(self, kwargs):
        return kwargs[2:]

    def _is_varargs(self, arg):
        return arg.startswith('*')

    def _is_kw_only_separator(self, arg):
        return arg == '*'

    def _format_varargs(self, varargs):
        return varargs[1:]


class UserKeywordArgumentParser(_ArgumentSpecParser):

    def _validate_arg(self, arg):
        arg, default = split_from_equals(arg)
        if not (is_assign(arg) or arg == '@{}'):
            self._report_error("Invalid argument syntax '%s'." % arg)
        if default is None:
            return arg
        if not is_scalar_assign(arg):
            typ = 'list' if arg[0] == '@' else 'dictionary'
            self._report_error("Only normal arguments accept default values, "
                               "%s arguments like '%s' do not." % (typ, arg))
        return arg, default

    def _is_kwargs(self, arg):
        return arg and arg[0] == '&'

    def _format_kwargs(self, kwargs):
        return kwargs[2:-1]

    def _is_varargs(self, arg):
        return arg and arg[0] == '@'

    def _is_kw_only_separator(self, arg):
        return arg == '@{}'

    def _format_varargs(self, varargs):
        return varargs[2:-1]

    def _format_arg(self, arg):
        return arg[2:-1]
