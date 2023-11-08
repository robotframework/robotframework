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
from enum import Enum
from typing import Any

from robot.utils import NOT_SET, safe_str, setter

from .argumentconverter import ArgumentConverter
from .argumentmapper import ArgumentMapper
from .argumentresolver import ArgumentResolver
from .typeinfo import TypeInfo
from .typevalidator import TypeValidator


class ArgumentSpec:

    def __init__(self, name=None, type='Keyword', positional_only=None,
                 positional_or_named=None, var_positional=None, named_only=None,
                 var_named=None, embedded=None, defaults=None, types=None):
        self.name = name
        self.type = type
        # FIXME: Use tuples, not lists. Consider using __slots__.
        self.positional_only = positional_only or []
        self.positional_or_named = positional_or_named or []
        self.var_positional = var_positional
        self.named_only = named_only or []
        self.var_named = var_named
        self.embedded = embedded or ()
        self.defaults = defaults or {}
        self.types = types

    @setter
    def types(self, types) -> 'dict[str, TypeInfo]':
        return TypeValidator(self).validate(types)

    @property
    def positional(self):
        return self.positional_only + self.positional_or_named

    @property
    def named(self):
        return self.named_only + self.positional_or_named

    @property
    def minargs(self):
        return len([arg for arg in self.positional if arg not in self.defaults])

    @property
    def maxargs(self):
        return len(self.positional) if not self.var_positional else sys.maxsize

    @property
    def argument_names(self):
        return (self.positional_only +
                self.positional_or_named +
                ([self.var_positional] if self.var_positional else []) +
                self.named_only +
                ([self.var_named] if self.var_named else []))

    def resolve(self, arguments, variables=None, converters=None,
                resolve_named=True, resolve_variables_until=None,
                dict_to_kwargs=False, languages=None):
        resolver = ArgumentResolver(self, resolve_named,
                                    resolve_variables_until, dict_to_kwargs)
        positional, named = resolver.resolve(arguments, variables)
        return self.convert(positional, named, converters, dry_run=not variables,
                            languages=languages)

    def convert(self, positional, named, converters=None, dry_run=False, languages=None):
        if self.types or self.defaults:
            converter = ArgumentConverter(self, converters, dry_run, languages)
            positional, named = converter.convert(positional, named)
        return positional, named

    def map(self, positional, named, replace_defaults=True):
        mapper = ArgumentMapper(self)
        return mapper.map(positional, named, replace_defaults)

    def __iter__(self):
        get_type = (self.types or {}).get
        get_default = self.defaults.get
        for arg in self.positional_only:
            yield ArgInfo(ArgInfo.POSITIONAL_ONLY, arg,
                          get_type(arg), get_default(arg, NOT_SET))
        if self.positional_only:
            yield ArgInfo(ArgInfo.POSITIONAL_ONLY_MARKER)
        for arg in self.positional_or_named:
            yield ArgInfo(ArgInfo.POSITIONAL_OR_NAMED, arg,
                          get_type(arg), get_default(arg, NOT_SET))
        if self.var_positional:
            yield ArgInfo(ArgInfo.VAR_POSITIONAL, self.var_positional,
                          get_type(self.var_positional))
        elif self.named_only:
            yield ArgInfo(ArgInfo.NAMED_ONLY_MARKER)
        for arg in self.named_only:
            yield ArgInfo(ArgInfo.NAMED_ONLY, arg,
                          get_type(arg), get_default(arg, NOT_SET))
        if self.var_named:
            yield ArgInfo(ArgInfo.VAR_NAMED, self.var_named,
                          get_type(self.var_named))

    def __bool__(self):
        return any([self.positional_only, self.positional_or_named, self.var_positional,
                    self.named_only, self.var_named])

    def __str__(self):
        return ', '.join(str(arg) for arg in self)


class ArgInfo:
    """Contains argument information. Only used by Libdoc."""
    POSITIONAL_ONLY = 'POSITIONAL_ONLY'
    POSITIONAL_ONLY_MARKER = 'POSITIONAL_ONLY_MARKER'
    POSITIONAL_OR_NAMED = 'POSITIONAL_OR_NAMED'
    VAR_POSITIONAL = 'VAR_POSITIONAL'
    NAMED_ONLY_MARKER = 'NAMED_ONLY_MARKER'
    NAMED_ONLY = 'NAMED_ONLY'
    VAR_NAMED = 'VAR_NAMED'

    def __init__(self, kind: str,
                 name: str = '',
                 type: 'TypeInfo|None' = None,
                 default: Any = NOT_SET):
        self.kind = kind
        self.name = name
        self.type = type or TypeInfo()
        self.default = default

    @property
    def required(self):
        if self.kind in (self.POSITIONAL_ONLY,
                         self.POSITIONAL_OR_NAMED,
                         self.NAMED_ONLY):
            return self.default is NOT_SET
        return False

    @property
    def default_repr(self):
        if self.default is NOT_SET:
            return None
        if isinstance(self.default, Enum):
            return self.default.name
        return safe_str(self.default)

    def __str__(self):
        if self.kind == self.POSITIONAL_ONLY_MARKER:
            return '/'
        if self.kind == self.NAMED_ONLY_MARKER:
            return '*'
        ret = self.name
        if self.kind == self.VAR_POSITIONAL:
            ret = '*' + ret
        elif self.kind == self.VAR_NAMED:
            ret = '**' + ret
        if self.type:
            ret = f'{ret}: {self.type}'
            default_sep = ' = '
        else:
            default_sep = '='
        if self.default is not NOT_SET:
            ret = f'{ret}{default_sep}{self.default_repr}'
        return ret
