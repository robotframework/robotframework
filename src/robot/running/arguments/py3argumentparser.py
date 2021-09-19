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

from inspect import signature, Parameter
import typing

from .argumentspec import ArgumentSpec


class PythonArgumentParser:

    def __init__(self, type='Keyword'):
        self._type = type

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
        robot_types = getattr(handler, 'robot_types', ())
        if robot_types or robot_types is None:
            spec.types = robot_types
        else:
            spec.types = self._get_type_hints(handler, spec)

    def _get_type_hints(self, handler, spec):
        try:
            type_hints = typing.get_type_hints(handler)
        except Exception:  # Can raise pretty much anything
            # Handle weird (C based?) functions without annotations.
            # https://github.com/robotframework/robotframework/issues/4059
            return getattr(handler, '__annotations__', {})
        self._remove_mismatching_type_hints(type_hints, spec.argument_names)
        return type_hints

    # TODO: This is likely not needed nowadays because we unwrap keywords.
    # Don't want to remove in 4.1.x but can go in 5.0.
    def _remove_mismatching_type_hints(self, type_hints, argument_names):
        # typing.get_type_hints returns info from the original function even
        # if it is decorated. Argument names are got from the wrapping
        # decorator and thus there is a mismatch that needs to be resolved.
        mismatch = set(type_hints) - set(argument_names)
        for name in mismatch:
            type_hints.pop(name)
