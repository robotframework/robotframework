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

import sys

from robot.utils import setter

from .argumentconverter import ArgumentConverter
from .argumentmapper import ArgumentMapper
from .argumentresolver import ArgumentResolver
from .typevalidator import TypeValidator


class ArgumentSpec(object):

    def __init__(self, name=None, type='Keyword', positional=None,
                 varargs=None, kwonlyargs=None, kwargs=None, defaults=None,
                 types=None, supports_named=True):
        self.name = name
        self.type = type
        self.positional = positional or []
        self.varargs = varargs
        self.kwonlyargs = kwonlyargs or []
        self.kwargs = kwargs
        self.defaults = defaults or {}
        self.types = types
        self.supports_named = supports_named

    @setter
    def types(self, types):
        return TypeValidator(self).validate(types)

    @property
    def minargs(self):
        required = [arg for arg in self.positional if arg not in self.defaults]
        return len(required)

    @property
    def maxargs(self):
        return len(self.positional) if not self.varargs else sys.maxsize

    @property
    def argument_names(self):
        return (self.positional + ([self.varargs] if self.varargs else []) +
                self.kwonlyargs + ([self.kwargs] if self.kwargs else []))

    def resolve(self, arguments, variables=None, resolve_named=True,
                resolve_variables_until=None, dict_to_kwargs=False):
        resolver = ArgumentResolver(self, resolve_named,
                                    resolve_variables_until, dict_to_kwargs)
        positional, named = resolver.resolve(arguments, variables)
        if self.types or self.defaults:
            converter = ArgumentConverter(self, dry_run=not variables)
            positional, named = converter.convert(positional, named)
        return positional, named

    def map(self, positional, named, replace_defaults=True):
        mapper = ArgumentMapper(self)
        return mapper.map(positional, named, replace_defaults)
