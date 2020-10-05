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
import sys
try:
    from enum import Enum
except ImportError:    # Standard in Py 3.4+ but can be separately installed
    class Enum(object):
        pass

from robot.utils import setter, py2to3, unicode, unic

from .argumentconverter import ArgumentConverter
from .argumentmapper import ArgumentMapper
from .argumentresolver import ArgumentResolver
from .typevalidator import TypeValidator


@py2to3
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

    def __iter__(self):
        notset = ArgInfo.NOTSET
        get_type = (self.types or {}).get
        get_default = self.defaults.get
        for arg in self.positional:
            yield ArgInfo(ArgInfo.POSITIONAL_OR_KEYWORD, arg,
                          get_type(arg, notset), get_default(arg, notset))
        if self.varargs:
            yield ArgInfo(ArgInfo.VAR_POSITIONAL, self.varargs,
                          get_type(self.varargs, notset))
        elif self.kwonlyargs:
            yield ArgInfo(ArgInfo.KEYWORD_ONLY_MARKER)
        for arg in self.kwonlyargs:
            yield ArgInfo(ArgInfo.KEYWORD_ONLY, arg,
                          get_type(arg, notset), get_default(arg, notset))
        if self.kwargs:
            yield ArgInfo(ArgInfo.VAR_KEYWORD, self.kwargs,
                          get_type(self.kwargs, notset))

    def __unicode__(self):
        return ', '.join(unicode(arg) for arg in self)


@py2to3
class ArgInfo(object):
    NOTSET = object()
    POSITIONAL_OR_KEYWORD = 'POSITIONAL_OR_KEYWORD'
    VAR_POSITIONAL = 'VAR_POSITIONAL'
    KEYWORD_ONLY_MARKER = 'KEYWORD_ONLY_MARKER'
    KEYWORD_ONLY = 'KEYWORD_ONLY'
    VAR_KEYWORD = 'VAR_KEYWORD'

    def __init__(self, kind, name='', type=NOTSET, default=NOTSET):
        self.kind = kind
        self.name = name
        self.type = type
        self.default = default

    @property
    def required(self):
        if self.kind in (self.POSITIONAL_OR_KEYWORD, self.KEYWORD_ONLY):
            return self.default is self.NOTSET
        return False

    @property
    def type_string(self):
        if self.type is self.NOTSET:
            return 'NOTSET'
        if not isclass(self.type):
            return self.type
        if issubclass(self.type, Enum):
            return self._format_enum(self.type)
        return self.type.__name__

    def _format_enum(self, enum):
        try:
            members = list(enum.__members__)
        except AttributeError:  # old enum module
            members = [attr for attr in dir(enum) if not attr.startswith('_')]
        while len(members) > 3 and len(' | '.join(members)) > 42:
            members[-2:] = ['...']
        return '%s { %s }' % (enum.__name__, ' | '.join(members))

    def __unicode__(self):
        if self.kind == self.KEYWORD_ONLY_MARKER:
            return '*'
        ret = self.name
        if self.kind == self.VAR_POSITIONAL:
            ret = '*' + ret
        elif self.kind == self.VAR_KEYWORD:
            ret = '**' + ret
        if self.type is not self.NOTSET:
            ret = '%s: %s' % (ret, self.type_string)
            default_sep = ' = '
        else:
            default_sep = '='
        if self.default is not self.NOTSET:
            ret = '%s%s%s' % (ret, default_sep, unic(self.default))
        return ret
