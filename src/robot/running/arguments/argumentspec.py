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
from typing import Any, Callable, Iterator, Mapping, Sequence

from robot.utils import NOT_SET, safe_str, setter, SetterAwareType

from .argumentconverter import ArgumentConverter
from .argumentmapper import ArgumentMapper
from .argumentresolver import ArgumentResolver
from .typeinfo import TypeInfo
from .typevalidator import TypeValidator


class ArgumentSpec(metaclass=SetterAwareType):
    __slots__ = (
        "_name",
        "type",
        "positional_only",
        "positional_or_named",
        "var_positional",
        "named_only",
        "var_named",
        "embedded",
        "defaults",
    )

    def __init__(
        self,
        name: "str|Callable[[], str]|None" = None,
        type: str = "Keyword",
        positional_only: Sequence[str] = (),
        positional_or_named: Sequence[str] = (),
        var_positional: "str|None" = None,
        named_only: Sequence[str] = (),
        var_named: "str|None" = None,
        defaults: "Mapping[str, Any]|None" = None,
        embedded: Sequence[str] = (),
        types: "Mapping|Sequence|None" = None,
        return_type: "TypeInfo|None" = None,
    ):
        self.name = name
        self.type = type
        self.positional_only = tuple(positional_only)
        self.positional_or_named = tuple(positional_or_named)
        self.var_positional = var_positional
        self.named_only = tuple(named_only)
        self.var_named = var_named
        self.embedded = tuple(embedded)
        self.defaults = defaults or {}
        self.types = types
        self.return_type = return_type

    @property
    def name(self) -> "str|None":
        return self._name if not callable(self._name) else self._name()

    @name.setter
    def name(self, name: "str|Callable[[], str]|None"):
        self._name = name

    @setter
    def types(self, types: "Mapping|Sequence|None") -> "dict[str, TypeInfo]|None":
        return TypeValidator(self).validate(types)

    @setter
    def return_type(self, hint) -> "TypeInfo|None":
        if hint in (None, type(None)):
            return None
        if isinstance(hint, TypeInfo):
            return hint
        return TypeInfo.from_type_hint(hint)

    @property
    def positional(self) -> "tuple[str, ...]":
        return self.positional_only + self.positional_or_named

    @property
    def named(self) -> "tuple[str, ...]":
        return self.named_only + self.positional_or_named

    @property
    def minargs(self) -> int:
        return len([arg for arg in self.positional if arg not in self.defaults])

    @property
    def maxargs(self) -> int:
        return len(self.positional) if not self.var_positional else sys.maxsize

    @property
    def argument_names(self) -> "tuple[str, ...]":
        var_positional = (self.var_positional,) if self.var_positional else ()
        var_named = (self.var_named,) if self.var_named else ()
        return (
            self.positional_only
            + self.positional_or_named
            + var_positional
            + self.named_only
            + var_named
        )

    def resolve(
        self,
        args,
        named_args=None,
        variables=None,
        converters=None,
        resolve_named=True,
        resolve_args_until=None,
        dict_to_kwargs=False,
        languages=None,
    ) -> "tuple[list, list]":
        resolver = ArgumentResolver(
            self,
            resolve_named,
            resolve_args_until,
            dict_to_kwargs,
        )
        positional, named = resolver.resolve(args, named_args, variables)
        return self.convert(
            positional,
            named,
            converters,
            dry_run=not variables,
            languages=languages,
        )

    def convert(
        self,
        positional,
        named,
        converters=None,
        dry_run=False,
        languages=None,
    ) -> "tuple[list, list]":
        if self.types or self.defaults:
            converter = ArgumentConverter(self, converters, dry_run, languages)
            positional, named = converter.convert(positional, named)
        return positional, named

    def map(
        self,
        positional,
        named,
        replace_defaults=True,
    ) -> "tuple[list, list]":
        mapper = ArgumentMapper(self)
        return mapper.map(positional, named, replace_defaults)

    def copy(self) -> "ArgumentSpec":
        types = dict(self.types) if self.types is not None else None
        return type(self)(
            self.name,
            self.type,
            self.positional_only,
            self.positional_or_named,
            self.var_positional,
            self.named_only,
            self.var_named,
            dict(self.defaults),
            self.embedded,
            types,
            self.return_type,
        )

    def __iter__(self) -> Iterator["ArgInfo"]:
        get_type = (self.types or {}).get
        get_default = self.defaults.get
        for arg in self.positional_only:
            yield ArgInfo(
                ArgInfo.POSITIONAL_ONLY,
                arg,
                get_type(arg),
                get_default(arg, NOT_SET),
            )
        if self.positional_only:
            yield ArgInfo(ArgInfo.POSITIONAL_ONLY_MARKER)
        for arg in self.positional_or_named:
            yield ArgInfo(
                ArgInfo.POSITIONAL_OR_NAMED,
                arg,
                get_type(arg),
                get_default(arg, NOT_SET),
            )
        if self.var_positional:
            yield ArgInfo(
                ArgInfo.VAR_POSITIONAL,
                self.var_positional,
                get_type(self.var_positional),
            )
        elif self.named_only:
            yield ArgInfo(ArgInfo.NAMED_ONLY_MARKER)
        for arg in self.named_only:
            yield ArgInfo(
                ArgInfo.NAMED_ONLY,
                arg,
                get_type(arg),
                get_default(arg, NOT_SET),
            )
        if self.var_named:
            yield ArgInfo(
                ArgInfo.VAR_NAMED,
                self.var_named,
                get_type(self.var_named),
            )

    def __bool__(self):
        return any(self)

    def __str__(self):
        return ", ".join(str(arg) for arg in self)


class ArgInfo:
    """Contains argument information. Only used by Libdoc."""

    POSITIONAL_ONLY = "POSITIONAL_ONLY"
    POSITIONAL_ONLY_MARKER = "POSITIONAL_ONLY_MARKER"
    POSITIONAL_OR_NAMED = "POSITIONAL_OR_NAMED"
    VAR_POSITIONAL = "VAR_POSITIONAL"
    NAMED_ONLY_MARKER = "NAMED_ONLY_MARKER"
    NAMED_ONLY = "NAMED_ONLY"
    VAR_NAMED = "VAR_NAMED"

    def __init__(
        self,
        kind: str,
        name: str = "",
        type: "TypeInfo|None" = None,
        default: Any = NOT_SET,
    ):
        self.kind = kind
        self.name = name
        self.type = type or TypeInfo()
        self.default = default

    @property
    def required(self) -> bool:
        if self.kind in (
            self.POSITIONAL_ONLY,
            self.POSITIONAL_OR_NAMED,
            self.NAMED_ONLY,
        ):
            return self.default is NOT_SET
        return False

    @property
    def default_repr(self) -> "str|None":
        if self.default is NOT_SET:
            return None
        if isinstance(self.default, Enum):
            return self.default.name
        return safe_str(self.default)

    def __str__(self):
        if self.kind == self.POSITIONAL_ONLY_MARKER:
            return "/"
        if self.kind == self.NAMED_ONLY_MARKER:
            return "*"
        ret = self.name
        if self.kind == self.VAR_POSITIONAL:
            ret = "*" + ret
        elif self.kind == self.VAR_NAMED:
            ret = "**" + ret
        if self.type:
            ret = f"{ret}: {self.type}"
            default_sep = " = "
        else:
            default_sep = "="
        if self.default is not NOT_SET:
            ret = f"{ret}{default_sep}{self.default_repr}"
        return ret
