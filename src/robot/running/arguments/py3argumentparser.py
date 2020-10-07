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

import inspect
import typing

from robot.utils import PY_VERSION

from .argumentspec import ArgumentSpec


class PythonArgumentParser:

    def __init__(self, type='Keyword'):
        self._type = type

    def parse(self, handler, name=None):
        positional, varargs, kwonly, kwargs, defaults = self._get_arg_spec(handler)
        spec = ArgumentSpec(
            name,
            self._type,
            positional_or_named=positional,
            var_positional=varargs,
            named_only=kwonly,
            var_named=kwargs,
            defaults=defaults
        )
        spec.types = self._get_types(handler, spec)
        return spec

    def _get_arg_spec(self, handler):
        try:
            signature = inspect.signature(handler)
        except ValueError:    # Can occur w/ C functions (incl. many builtins).
            return [], 'args', [], None, {}
        parameters = list(signature.parameters.values())
        # `inspect.signature` drops `self` with bound methods and that's the case when
        # inspecting keywords. `__init__` is got directly from class (i.e. isn't bound)
        # so we need to handle that case ourselves.
        if handler.__name__ == '__init__':
            parameters = parameters[1:]
        return self._parse_params(parameters)

    def _parse_params(self, parameters):
        positional = []
        varargs = None
        kwonly = []
        kwargs = None
        defaults = {}
        for param in parameters:
            if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
                positional.append(param.name)
            elif param.kind == param.VAR_POSITIONAL:
                varargs = param.name
            elif param.kind == param.KEYWORD_ONLY:
                kwonly.append(param.name)
            elif param.kind == param.VAR_KEYWORD:
                kwargs = param.name
            if param.default is not param.empty:
                defaults[param.name] = param.default
        return positional, varargs, kwonly, kwargs, defaults

    def _get_types(self, handler, spec):
        types = getattr(handler, 'robot_types', ())
        # If types are set using the `@keyword` decorator, use them. Including when
        # types are explicitly disabled with `@keyword(types=None)`.
        if types or types is None:
            return types
        return self._get_type_hints(handler, spec)

    def _get_type_hints(self, handler, spec):
        try:
            type_hints = typing.get_type_hints(handler)
        except Exception:  # Can raise pretty much anything
            return handler.__annotations__
        self._remove_mismatching_type_hints(type_hints, spec.argument_names)
        self._remove_optional_none_type_hints(type_hints, spec.defaults)
        return type_hints

    def _remove_mismatching_type_hints(self, type_hints, argument_names):
        # typing.get_type_hints returns info from the original function even
        # if it is decorated. Argument names are got from the wrapping
        # decorator and thus there is a mismatch that needs to be resolved.
        mismatch = set(type_hints) - set(argument_names)
        for name in mismatch:
            type_hints.pop(name)

    def _remove_optional_none_type_hints(self, type_hints, defaults):
        # If argument has None as a default, typing.get_type_hints adds
        # optional None to the information it returns. We don't want that.
        for arg in defaults:
            if defaults[arg] is None and arg in type_hints:
                type_ = type_hints[arg]
                if self._is_union(type_):
                    try:
                        types = type_.__args__
                    except AttributeError:
                        # Python 3.5.2's typing uses __union_params__ instead
                        # of __args__. This block can likely be safely removed
                        # when Python 3.5 support is dropped
                        types = type_.__union_params__
                    if len(types) == 2 and types[1] is type(None):
                        type_hints[arg] = types[0]

    def _is_union(self, type_):
        if PY_VERSION >= (3, 7) and hasattr(type_, '__origin__'):
            type_ = type_.__origin__
        return isinstance(type_, type(typing.Union))
