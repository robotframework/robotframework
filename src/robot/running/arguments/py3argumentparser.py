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

from inspect import getfullargspec, ismethod, unwrap
import typing

from robot.utils import PY_VERSION

from .argumentspec import ArgumentSpec


class PythonArgumentParser:

    def __init__(self, type='Keyword'):
        self._type = type

    def parse(self, handler, name=None):
        args, varargs, kws, defaults, kwo, kwo_defaults, annotations \
                = self._get_arg_spec(handler)
        if ismethod(handler) or handler.__name__ == '__init__':
            args = args[1:]    # Drop 'self'.
        spec = ArgumentSpec(
            name,
            self._type,
            positional=args,
            varargs=varargs,
            kwargs=kws,
            kwonlyargs=kwo,
            defaults=self._get_defaults(args, defaults, kwo_defaults)
        )
        spec.types = self._get_types(handler, annotations, spec)
        return spec

    def _get_arg_spec(self, handler):
        handler = unwrap(handler)
        try:
            if handler.__name__ == 'po':
                print(getfullargspec(handler))
            return getfullargspec(handler)
        except TypeError:    # Can occur w/ C functions (incl. many builtins).
            return [], 'args', None, None, [], None, {}

    def _get_defaults(self, args, default_values, kwo_defaults):
        if default_values:
            defaults = dict(zip(args[-len(default_values):], default_values))
        else:
            defaults = {}
        if kwo_defaults:
            defaults.update(kwo_defaults)
        return defaults

    def _get_types(self, handler, annotations, spec):
        types = getattr(handler, 'robot_types', ())
        if types is None:
            return None
        if types:
            return types
        return self._get_type_hints(handler, annotations, spec)

    def _get_type_hints(self, handler, annotations, spec):
        try:
            type_hints = typing.get_type_hints(handler)
        except Exception:  # Can raise pretty much anything
            return annotations
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
