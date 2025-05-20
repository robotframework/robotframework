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
from os.path import normpath
from pathlib import Path
from typing import Any, Callable, Generic, Mapping, Sequence, TYPE_CHECKING, TypeVar

from robot.errors import DataError
from robot.model import Tags
from robot.utils import (
    is_init, is_list_like, printable_name, split_tags_from_doc, type_name
)

from .arguments import ArgumentSpec, DynamicArgumentParser, PythonArgumentParser
from .dynamicmethods import (
    GetKeywordArguments, GetKeywordDocumentation, GetKeywordSource, GetKeywordTags,
    GetKeywordTypes, RunKeyword
)
from .keywordimplementation import KeywordImplementation
from .librarykeywordrunner import (
    EmbeddedArgumentsRunner, LibraryKeywordRunner, RunKeywordRunner
)
from .model import BodyItemParent, Keyword
from .runkwregister import RUN_KW_REGISTER

if TYPE_CHECKING:
    from robot.conf import LanguagesLike

    from .testlibraries import DynamicLibrary, TestLibrary


Self = TypeVar("Self", bound="LibraryKeyword")
K = TypeVar("K", bound="LibraryKeyword")


class LibraryKeyword(KeywordImplementation):
    """Base class for different library keywords."""

    type = KeywordImplementation.LIBRARY_KEYWORD
    owner: "TestLibrary"
    __slots__ = ("_resolve_args_until",)

    def __init__(
        self,
        owner: "TestLibrary",
        name: str = "",
        args: "ArgumentSpec|None" = None,
        doc: str = "",
        tags: "Tags|Sequence[str]" = (),
        resolve_args_until: "int|None" = None,
        parent: "BodyItemParent|None" = None,
        error: "str|None" = None,
    ):
        super().__init__(name, args, doc, tags, owner=owner, parent=parent, error=error)
        self._resolve_args_until = resolve_args_until

    @property
    def method(self) -> Callable[..., Any]:
        raise NotImplementedError

    @property
    def lineno(self) -> "int|None":
        method = self.method
        try:
            lines, start_lineno = inspect.getsourcelines(inspect.unwrap(method))
        except (TypeError, OSError, IOError):
            return None
        for increment, line in enumerate(lines):
            if line.strip().startswith("def "):
                return start_lineno + increment
        return start_lineno

    def create_runner(
        self,
        name: "str|None",
        languages: "LanguagesLike" = None,
    ) -> LibraryKeywordRunner:
        if self.embedded:
            return EmbeddedArgumentsRunner(self, name)
        if self._resolve_args_until is not None:
            dry_run = RUN_KW_REGISTER.get_dry_run(self.owner.real_name, self.name)
            return RunKeywordRunner(self, dry_run_children=dry_run)
        return LibraryKeywordRunner(self, languages=languages)

    def resolve_arguments(
        self,
        args: "Sequence[str|Any]",
        named_args: "Mapping[str, Any]|None" = None,
        variables=None,
        languages: "LanguagesLike" = None,
    ) -> "tuple[list, list]":
        resolve_args_until = self._resolve_args_until
        positional, named = self.args.resolve(
            args,
            named_args,
            variables,
            self.owner.converters,
            resolve_named=resolve_args_until is None,
            resolve_args_until=resolve_args_until,
            languages=languages,
        )
        if self.embedded:
            self.embedded.validate(positional)
        return positional, named

    def bind(self: Self, data: Keyword) -> Self:
        return self.copy(parent=data.parent)

    def copy(self: Self, **attributes) -> Self:
        raise NotImplementedError


class StaticKeyword(LibraryKeyword):
    """Represents a keyword in a static library."""

    __slots__ = ("method_name",)

    def __init__(
        self,
        method_name: str,
        owner: "TestLibrary",
        name: str = "",
        args: "ArgumentSpec|None" = None,
        doc: str = "",
        tags: "Tags|Sequence[str]" = (),
        resolve_args_until: "int|None" = None,
        parent: "BodyItemParent|None" = None,
        error: "str|None" = None,
    ):
        super().__init__(
            owner,
            name,
            args,
            doc,
            tags,
            resolve_args_until,
            parent,
            error,
        )
        self.method_name = method_name

    @property
    def method(self) -> Callable[..., Any]:
        """Keyword method."""
        return getattr(self.owner.instance, self.method_name)

    @property
    def source(self) -> "Path|None":
        # `getsourcefile` can return None and raise TypeError.
        try:
            if self.method is None:
                raise TypeError
            source = inspect.getsourcefile(inspect.unwrap(self.method))
        except TypeError:
            source = None
        return Path(normpath(source)) if source else super().source

    @classmethod
    def from_name(cls, name: str, owner: "TestLibrary") -> "StaticKeyword":
        return StaticKeywordCreator(name, owner).create(method_name=name)

    def copy(self, **attributes) -> "StaticKeyword":
        return StaticKeyword(
            self.method_name,
            self.owner,
            self.name,
            self.args,
            self._doc,
            self.tags,
            self._resolve_args_until,
            self.parent,
            self.error,
        ).config(**attributes)


class DynamicKeyword(LibraryKeyword):
    """Represents a keyword in a dynamic library."""

    owner: "DynamicLibrary"
    __slots__ = ("run_keyword", "_orig_name", "__source_info")

    def __init__(
        self,
        owner: "DynamicLibrary",
        name: str = "",
        args: "ArgumentSpec|None" = None,
        doc: str = "",
        tags: "Tags|Sequence[str]" = (),
        resolve_args_until: "int|None" = None,
        parent: "BodyItemParent|None" = None,
        error: "str|None" = None,
    ):
        # TODO: It would probably be better not to convert name we got from
        # `get_keyword_names`. That would have some backwards incompatibility
        # effects, but we can consider it in RF 8.0.
        super().__init__(
            owner,
            printable_name(name, code_style=True),
            args,
            doc,
            tags,
            resolve_args_until,
            parent,
            error,
        )
        self._orig_name = name
        self.__source_info = None

    @property
    def method(self) -> Callable[..., Any]:
        """Dynamic ``run_keyword`` method."""
        return RunKeyword(
            self.owner.instance,
            self._orig_name,
            self.owner.supports_named_args,
        )

    @property
    def source(self) -> "Path|None":
        return self._source_info[0] or super().source

    @property
    def lineno(self) -> "int|None":
        return self._source_info[1]

    @property
    def _source_info(self) -> "tuple[Path|None, int]":
        if not self.__source_info:
            get_keyword_source = GetKeywordSource(self.owner.instance)
            try:
                source = get_keyword_source(self._orig_name)
            except DataError as err:
                source = None
                self.owner.report_error(
                    f"Getting source information for keyword '{self.name}' "
                    f"failed: {err}",
                    err.details,
                )
            if source and ":" in source and source.rsplit(":", 1)[1].isdigit():
                source, lineno = source.rsplit(":", 1)
                lineno = int(lineno)
            else:
                lineno = None
            self.__source_info = Path(normpath(source)) if source else None, lineno
        return self.__source_info

    @classmethod
    def from_name(cls, name: str, owner: "DynamicLibrary") -> "DynamicKeyword":
        return DynamicKeywordCreator(name, owner).create()

    def resolve_arguments(
        self,
        args: "Sequence[str|Any]",
        named_args: "Mapping[str, Any]|None" = None,
        variables=None,
        languages: "LanguagesLike" = None,
    ) -> "tuple[list, list]":
        positional, named = super().resolve_arguments(
            args,
            named_args,
            variables,
            languages,
        )
        if not self.owner.supports_named_args:
            positional, named = self.args.map(positional, named)
        return positional, named

    def copy(self, **attributes) -> "DynamicKeyword":
        return DynamicKeyword(
            self.owner,
            self._orig_name,
            self.args,
            self._doc,
            self.tags,
            self._resolve_args_until,
            self.parent,
            self.error,
        ).config(**attributes)


class LibraryInit(LibraryKeyword):
    """Represents a library initializer.

    :attr:`positional` and :attr:`named` contain arguments used for initializing
    the library.
    """

    def __init__(
        self,
        owner: "TestLibrary",
        name: str = "",
        args: "ArgumentSpec|None" = None,
        doc: str = "",
        tags: "Tags|Sequence[str]" = (),
        positional: "list|None" = None,
        named: "dict|None" = None,
    ):
        super().__init__(owner, name, args, doc, tags)
        self.positional = positional or []
        self.named = named or {}

    @property
    def doc(self) -> str:
        from .testlibraries import DynamicLibrary

        if isinstance(self.owner, DynamicLibrary):
            doc = GetKeywordDocumentation(self.owner.instance)("__init__")
            if doc:
                return doc
        return self._doc

    @doc.setter
    def doc(self, doc: str):
        self._doc = doc

    @property
    def method(self) -> "Callable[..., None]|None":
        """Initializer method.

        ``None`` with module based libraries and when class based libraries
        do not have ``__init__``.
        """
        return getattr(self.owner.instance, "__init__", None)

    @classmethod
    def from_class(cls, klass) -> "LibraryInit":
        method = getattr(klass, "__init__", None)
        return LibraryInitCreator(method).create()

    @classmethod
    def null(cls) -> "LibraryInit":
        return LibraryInitCreator(None).create()

    def copy(self, **attributes) -> "LibraryInit":
        return LibraryInit(
            self.owner,
            self.name,
            self.args,
            self._doc,
            self.tags,
            self.positional,
            self.named,
        ).config(**attributes)


class KeywordCreator(Generic[K]):
    keyword_class: "type[K]"

    def __init__(self, name: str, library: "TestLibrary|None" = None):
        self.name = name
        self.library = library
        self.extra = {}
        if library and RUN_KW_REGISTER.is_run_keyword(library.real_name, name):
            resolve_until = RUN_KW_REGISTER.get_args_to_process(library.real_name, name)
            self.extra["resolve_args_until"] = resolve_until

    @property
    def instance(self) -> Any:
        return self.library.instance

    def create(self, **extra) -> K:
        tags = self.get_tags()
        doc, doc_tags = split_tags_from_doc(self.get_doc())
        kw = self.keyword_class(
            owner=self.library,
            name=self.get_name(),
            args=self.get_args(),
            doc=doc,
            tags=tags + doc_tags,
            **self.extra,
            **extra,
        )
        kw.args.name = lambda: kw.full_name
        return kw

    def get_name(self) -> str:
        raise NotImplementedError

    def get_args(self) -> ArgumentSpec:
        raise NotImplementedError

    def get_doc(self) -> str:
        raise NotImplementedError

    def get_tags(self) -> "list[str]":
        raise NotImplementedError


class StaticKeywordCreator(KeywordCreator[StaticKeyword]):
    keyword_class = StaticKeyword

    def __init__(self, name: str, library: "TestLibrary"):
        super().__init__(name, library)
        self.method = getattr(library.instance, name)

    def get_name(self) -> str:
        robot_name = getattr(self.method, "robot_name", None)
        name = robot_name or printable_name(self.name, code_style=True)
        if not name:
            raise DataError("Keyword name cannot be empty.")
        return name

    def get_args(self) -> ArgumentSpec:
        return PythonArgumentParser().parse(self.method)

    def get_doc(self) -> str:
        return inspect.getdoc(self.method) or ""

    def get_tags(self) -> "list[str]":
        tags = getattr(self.method, "robot_tags", ())
        if not is_list_like(tags):
            raise DataError(f"Expected tags to be list-like, got {type_name(tags)}.")
        return list(tags)


class DynamicKeywordCreator(KeywordCreator[DynamicKeyword]):
    keyword_class = DynamicKeyword
    library: "DynamicLibrary"

    def get_name(self) -> str:
        return self.name

    def get_args(self) -> ArgumentSpec:
        supports_named_args = self.library.supports_named_args
        get_keyword_arguments = GetKeywordArguments(self.instance, supports_named_args)
        spec = DynamicArgumentParser().parse(get_keyword_arguments(self.name))
        if not supports_named_args:
            name = RunKeyword(self.instance).name
            prefix = f"Too few '{name}' method parameters to support "
            if spec.named_only:
                raise DataError(prefix + "named-only arguments.")
            if spec.var_named:
                raise DataError(prefix + "free named arguments.")
        types = GetKeywordTypes(self.instance)(self.name)
        if isinstance(types, dict) and "return" in types:
            spec.return_type = types.pop("return")
        spec.types = types
        return spec

    def get_doc(self) -> str:
        return GetKeywordDocumentation(self.instance)(self.name)

    def get_tags(self) -> "list[str]":
        return GetKeywordTags(self.instance)(self.name)


class LibraryInitCreator(KeywordCreator[LibraryInit]):
    keyword_class = LibraryInit

    def __init__(self, method: "Callable[..., None]|None"):
        super().__init__("__init__")
        self.method = method if is_init(method) else lambda: None

    def create(self, **extra) -> LibraryInit:
        init = super().create(**extra)
        init.args.name = lambda: init.owner.name
        return init

    def get_name(self) -> str:
        return self.name

    def get_args(self) -> ArgumentSpec:
        return PythonArgumentParser("Library").parse(self.method)

    def get_doc(self) -> str:
        return inspect.getdoc(self.method) or ""

    def get_tags(self) -> "list[str]":
        return []
