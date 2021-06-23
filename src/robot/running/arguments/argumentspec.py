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

from inspect import isclass
import re
import sys

try:
    from typing import Union
except ImportError:
    class Union(object):
        pass

try:
    from enum import Enum
except ImportError:    # Standard in Py 3.4+ but can be separately installed
    class Enum(object):
        pass

from robot.utils import setter, py3to2, unicode, unic

from .argumentconverter import ArgumentConverter
from .argumentmapper import ArgumentMapper
from .argumentresolver import ArgumentResolver
from .typevalidator import TypeValidator


@py3to2
class ArgumentSpec(object):

    def __init__(self, name=None, type='Keyword', positional_only=None,
                 positional_or_named=None, var_positional=None, named_only=None,
                 var_named=None, defaults=None, types=None):
        self.name = name
        self.type = type
        self.positional_only = positional_only or []
        self.positional_or_named = positional_or_named or []
        self.var_positional = var_positional
        self.named_only = named_only or []
        self.var_named = var_named
        self.defaults = defaults or {}
        self.types = types

    @setter
    def types(self, types):
        return TypeValidator(self).validate(types)

    @property
    def positional(self):
        return self.positional_only + self.positional_or_named

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

    def __iter__(self):
        notset = ArgInfo.NOTSET
        get_type = (self.types or {}).get
        get_default = self.defaults.get
        for arg in self.positional_only:
            yield ArgInfo(ArgInfo.POSITIONAL_ONLY, arg,
                          get_type(arg, notset), get_default(arg, notset))
        if self.positional_only:
            yield ArgInfo(ArgInfo.POSITIONAL_ONLY_MARKER)
        for arg in self.positional_or_named:
            yield ArgInfo(ArgInfo.POSITIONAL_OR_NAMED, arg,
                          get_type(arg, notset), get_default(arg, notset))
        if self.var_positional:
            yield ArgInfo(ArgInfo.VAR_POSITIONAL, self.var_positional,
                          get_type(self.var_positional, notset))
        elif self.named_only:
            yield ArgInfo(ArgInfo.NAMED_ONLY_MARKER)
        for arg in self.named_only:
            yield ArgInfo(ArgInfo.NAMED_ONLY, arg,
                          get_type(arg, notset), get_default(arg, notset))
        if self.var_named:
            yield ArgInfo(ArgInfo.VAR_NAMED, self.var_named,
                          get_type(self.var_named, notset))

    def __bool__(self):
        return any([self.positional_only, self.positional_or_named, self.var_positional,
                    self.named_only, self.var_named])

    def __str__(self):
        return ', '.join(unicode(arg) for arg in self)


@py3to2
class ArgInfo(object):
    NOTSET = object()
    POSITIONAL_ONLY = 'POSITIONAL_ONLY'
    POSITIONAL_ONLY_MARKER = 'POSITIONAL_ONLY_MARKER'
    POSITIONAL_OR_NAMED = 'POSITIONAL_OR_NAMED'
    VAR_POSITIONAL = 'VAR_POSITIONAL'
    NAMED_ONLY_MARKER = 'NAMED_ONLY_MARKER'
    NAMED_ONLY = 'NAMED_ONLY'
    VAR_NAMED = 'VAR_NAMED'

    def __init__(self, kind, name='', types=NOTSET, default=NOTSET):
        self.kind = kind
        self.name = name
        self.types = types
        self.default = default

    @setter
    def types(self, typ):
        if not typ or typ is self.NOTSET:
            return tuple()
        if isinstance(typ, tuple):
            return typ
        if getattr(typ, '__origin__', None) is Union:
            return self._get_union_args(typ)
        return (typ,)

    def _get_union_args(self, union):
        try:
            return union.__args__
        except AttributeError:
            # Python 3.5.2's typing uses __union_params__ instead
            # of __args__. This block can likely be safely removed
            # when Python 3.5 support is dropped
            return union.__union_params__

    @property
    def required(self):
        if self.kind in (self.POSITIONAL_ONLY,
                         self.POSITIONAL_OR_NAMED,
                         self.NAMED_ONLY):
            return self.default is self.NOTSET
        return False

    @property
    def types_reprs(self):
        return [self._type_repr(t) for t in self.types]

    def _type_repr(self, typ):
        if typ is type(None):
            return 'None'
        if isclass(typ):
            return typ.__name__
        return re.sub(r'^typing\.(.+)', r'\1', unic(typ))

    @property
    def default_repr(self):
        if self.default is self.NOTSET:
            return None
        if isinstance(self.default, Enum):
            return self.default.name
        return unic(self.default)

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
        if self.types:
            ret = '%s: %s' % (ret, ' | '.join(self.types_reprs))
            default_sep = ' = '
        else:
            default_sep = '='
        if self.default is not self.NOTSET:
            ret = '%s%s%s' % (ret, default_sep, self.default_repr)
        return ret
