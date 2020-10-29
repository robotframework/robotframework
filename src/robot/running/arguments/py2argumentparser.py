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

from inspect import getargspec, ismethod

from .argumentspec import ArgumentSpec


class PythonArgumentParser(object):

    def __init__(self, type='Keyword'):
        self._type = type

    def parse(self, handler, name=None):
        try:
            args, varargs, kws, defaults = getargspec(handler)
        except TypeError:    # Can occur w/ C functions (incl. many builtins).
            args, varargs, kws, defaults = [], 'args', None, None
        if ismethod(handler) or handler.__name__ == '__init__':
            args = args[1:]    # Drop 'self'.
        spec = ArgumentSpec(
            name,
            self._type,
            positional_or_named=args,
            var_positional=varargs,
            var_named=kws,
            defaults=self._get_defaults(args, defaults),
            types=getattr(handler, 'robot_types', ())
        )
        return spec

    def _get_defaults(self, args, default_values):
        if not default_values:
            return {}
        return dict(zip(args[-len(default_values):], default_values))
