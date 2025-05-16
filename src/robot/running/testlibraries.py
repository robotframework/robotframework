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
from functools import cached_property, partial
from pathlib import Path
from types import ModuleType
from typing import Any, Literal, overload, Sequence, TypeVar

from robot.errors import DataError
from robot.libraries import STDLIBS
from robot.output import LOGGER
from robot.utils import (
    get_error_details, getdoc, Importer, is_dict_like, is_list_like, normalize,
    NormalizedDict, seq2str2, setter, type_name
)

from .arguments import CustomArgumentConverters
from .dynamicmethods import GetKeywordDocumentation, GetKeywordNames, RunKeyword
from .keywordfinder import KeywordFinder
from .librarykeyword import DynamicKeyword, LibraryInit, LibraryKeyword, StaticKeyword
from .libraryscopes import Scope, ScopeManager
from .outputcapture import OutputCapturer

Self = TypeVar("Self", bound="TestLibrary")


class TestLibrary:
    """Represents imported test library."""

    def __init__(
        self,
        code: "type|ModuleType",
        init: LibraryInit,
        name: "str|None" = None,
        real_name: "str|None" = None,
        source: "Path|None" = None,
        logger=LOGGER,
    ):
        self.code = code
        self.init = init
        self.init.owner = self
        self.instance = None
        self.name = name or code.__name__
        self.real_name = real_name or self.name
        self.source = source
        self._logger = logger
        self.keywords: list[LibraryKeyword] = []
        self._has_listeners = None
        self.scope_manager = ScopeManager.for_library(self)
        self.keyword_finder = KeywordFinder[LibraryKeyword](self)

    @property
    def instance(self) -> Any:
        """Current library instance.

        With module based libraries this is the module itself.

        With class based libraries this is an instance of the class. Instances are
        cleared automatically during execution based on their scope. Accessing this
        property creates a new instance if needed.

        :attr:`code` contains the original library code. With module based libraries
        it is the same as :attr:`instance`. With class based libraries it is
        the library class.
        """
        instance = self.code if self._instance is None else self._instance
        if self._has_listeners is None:
            self._has_listeners = self._instance_has_listeners(instance)
        return instance

    @instance.setter
    def instance(self, instance: Any):
        self._instance = instance

    @property
    def listeners(self) -> "list[Any]":
        if self._has_listeners is None:
            self._has_listeners = self._instance_has_listeners(self.instance)
        if self._has_listeners is False:
            return []
        listener = self.instance.ROBOT_LIBRARY_LISTENER
        return list(listener) if is_list_like(listener) else [listener]

    def _instance_has_listeners(self, instance) -> bool:
        return getattr(instance, "ROBOT_LIBRARY_LISTENER", None) is not None

    @property
    def converters(self) -> "CustomArgumentConverters|None":
        converters = getattr(self.code, "ROBOT_LIBRARY_CONVERTERS", None)
        if not converters:
            return None
        if not is_dict_like(converters):
            self.report_error(
                f"Argument converters must be given as a dictionary, "
                f"got {type_name(converters)}."
            )
            return None
        return CustomArgumentConverters.from_dict(converters, self)

    @property
    def doc(self) -> str:
        return getdoc(self.instance)

    @property
    def doc_format(self) -> str:
        return self._attr("ROBOT_LIBRARY_DOC_FORMAT", upper=True)

    @property
    def scope(self) -> Scope:
        scope = self._attr("ROBOT_LIBRARY_SCOPE", "TEST", upper=True)
        if scope == "GLOBAL":
            return Scope.GLOBAL
        if scope in ("SUITE", "TESTSUITE"):
            return Scope.SUITE
        return Scope.TEST

    @setter
    def source(self, source: "Path|str|None") -> "Path|None":
        return Path(source) if source else None

    @property
    def version(self) -> str:
        return self._attr("ROBOT_LIBRARY_VERSION") or self._attr("__version__")

    @property
    def lineno(self) -> int:
        return 1

    def _attr(self, name, default="", upper=False) -> str:
        value = str(getattr(self.code, name, default))
        if upper:
            value = normalize(value, ignore="_").upper()
        return value

    @classmethod
    def from_name(
        cls,
        name: str,
        real_name: "str|None" = None,
        args: "Sequence[str]|None" = None,
        variables=None,
        create_keywords: bool = True,
        logger=LOGGER,
    ) -> "TestLibrary":
        if name in STDLIBS:
            import_name = "robot.libraries." + name
        else:
            import_name = name
        if Path(name).exists():
            name = Path(name).stem
        with OutputCapturer(library_import=True):
            importer = Importer("library", logger=logger)
            code, source = importer.import_class_or_module(
                import_name, return_source=True
            )
        return cls.from_code(
            code, name, real_name, source, args, variables, create_keywords, logger
        )

    @classmethod
    def from_code(
        cls,
        code: "type|ModuleType",
        name: "str|None" = None,
        real_name: "str|None" = None,
        source: "Path|None" = None,
        args: "Sequence[str]|None" = None,
        variables=None,
        create_keywords: bool = True,
        logger=LOGGER,
    ) -> "TestLibrary":
        if inspect.ismodule(code):
            lib = cls.from_module(
                code, name, real_name, source, create_keywords, logger
            )
            if args:  # Resolving arguments reports an error.
                lib.init.resolve_arguments(args, variables=variables)
            return lib
        if args is None:
            args = ()
        return cls.from_class(
            code, name, real_name, source, args, variables, create_keywords, logger
        )

    @classmethod
    def from_module(
        cls,
        module: ModuleType,
        name: "str|None" = None,
        real_name: "str|None" = None,
        source: "Path|None" = None,
        create_keywords: bool = True,
        logger=LOGGER,
    ) -> "TestLibrary":
        return ModuleLibrary.from_module(
            module, name, real_name, source, create_keywords, logger
        )

    @classmethod
    def from_class(
        cls,
        klass: type,
        name: "str|None" = None,
        real_name: "str|None" = None,
        source: "Path|None" = None,
        args: Sequence[str] = (),
        variables=None,
        create_keywords: bool = True,
        logger=LOGGER,
    ) -> "TestLibrary":
        if not GetKeywordNames(klass):
            library = ClassLibrary
        elif not RunKeyword(klass):
            library = HybridLibrary
        else:
            library = DynamicLibrary
        return library.from_class(
            klass, name, real_name, source, args, variables, create_keywords, logger
        )

    def create_keywords(self):
        raise NotImplementedError

    @overload
    def find_keywords(
        self,
        name: str,
        count: Literal[1],
    ) -> LibraryKeyword: ...

    @overload
    def find_keywords(
        self,
        name: str,
        count: "int|None" = None,
    ) -> "list[LibraryKeyword]": ...

    def find_keywords(
        self,
        name: str,
        count: "int|None" = None,
    ) -> "list[LibraryKeyword]|LibraryKeyword":
        return self.keyword_finder.find(name, count)

    def copy(self: Self, name: str) -> Self:
        lib = type(self)(
            self.code,
            self.init.copy(),
            name,
            self.real_name,
            self.source,
            self._logger,
        )
        lib.instance = self.instance
        lib.keywords = [kw.copy(owner=lib) for kw in self.keywords]
        return lib

    def report_error(
        self,
        message: str,
        details: "str|None" = None,
        level: str = "ERROR",
        details_level: str = "INFO",
    ):
        prefix = "Error in" if level in ("ERROR", "WARN") else "In"
        self._logger.write(f"{prefix} library '{self.name}': {message}", level)
        if details:
            self._logger.write(f"Details:\n{details}", details_level)


class ModuleLibrary(TestLibrary):

    @property
    def scope(self) -> Scope:
        return Scope.GLOBAL

    @classmethod
    def from_module(
        cls,
        module: ModuleType,
        name: "str|None" = None,
        real_name: "str|None" = None,
        source: "Path|None" = None,
        create_keywords: bool = True,
        logger=LOGGER,
    ) -> "ModuleLibrary":
        library = cls(module, LibraryInit.null(), name, real_name, source, logger)
        if create_keywords:
            library.create_keywords()
        return library

    @classmethod
    def from_class(cls, *args, **kws) -> "TestLibrary":
        raise TypeError(f"Cannot create '{cls.__name__}' from class.")

    def create_keywords(self):
        includes = getattr(self.code, "__all__", None)
        StaticKeywordCreator(self, included_names=includes).create_keywords()


class ClassLibrary(TestLibrary):

    @property
    def instance(self) -> Any:
        if self._instance is None:
            positional, named = self.init.positional, self.init.named
            try:
                with OutputCapturer(library_import=True):
                    self._instance = self.code(*positional, **named)
            except Exception:
                message, details = get_error_details()
                if positional or named:
                    args = seq2str2(positional + [f"{n}={named[n]}" for n in named])
                    args_text = f"arguments {args}"
                else:
                    args_text = "no arguments"
                raise DataError(
                    f"Initializing library '{self.name}' with {args_text} "
                    f"failed: {message}\n{details}"
                )
        if self._has_listeners is None:
            self._has_listeners = self._instance_has_listeners(self._instance)
        return self._instance

    @instance.setter
    def instance(self, instance):
        self._instance = instance

    @property
    def lineno(self) -> int:
        try:
            lines, start_lineno = inspect.getsourcelines(self.code)
        except (TypeError, OSError, IOError):
            return 1
        for increment, line in enumerate(lines):
            if line.strip().startswith("class "):
                return start_lineno + increment
        return start_lineno

    @classmethod
    def from_module(cls, *args, **kws) -> "TestLibrary":
        raise TypeError(f"Cannot create '{cls.__name__}' from module.")

    @classmethod
    def from_class(
        cls,
        klass: type,
        name: "str|None" = None,
        real_name: "str|None" = None,
        source: "Path|None" = None,
        args: Sequence[str] = (),
        variables=None,
        create_keywords: bool = True,
        logger=LOGGER,
    ) -> "ClassLibrary":
        init = LibraryInit.from_class(klass)
        library = cls(klass, init, name, real_name, source, logger)
        positional, named = init.args.resolve(args, variables=variables)
        init.positional, init.named = list(positional), dict(named)
        if create_keywords:
            library.create_keywords()
        return library

    def create_keywords(self):
        StaticKeywordCreator(self, avoid_properties=True).create_keywords()


class HybridLibrary(ClassLibrary):

    def create_keywords(self):
        names = DynamicKeywordCreator(self).get_keyword_names()
        creator = StaticKeywordCreator(self, getting_method_failed_level="ERROR")
        creator.create_keywords(names)


class DynamicLibrary(ClassLibrary):
    _supports_named_args = None

    @property
    def supports_named_args(self) -> bool:
        if self._supports_named_args is None:
            self._supports_named_args = RunKeyword(self.instance).supports_named_args
        return self._supports_named_args

    @property
    def doc(self) -> str:
        return GetKeywordDocumentation(self.instance)("__intro__") or super().doc

    def create_keywords(self):
        DynamicKeywordCreator(self).create_keywords()


class KeywordCreator:

    def __init__(self, library: TestLibrary, getting_method_failed_level="INFO"):
        self.library = library
        self.getting_method_failed_level = getting_method_failed_level

    def get_keyword_names(self) -> "list[str]":
        raise NotImplementedError

    def create_keywords(self, names: "list[str]|None" = None):
        library = self.library
        library.keyword_finder.invalidate_cache()
        instance = library.instance
        keywords = library.keywords = []
        if names is None:
            names = self.get_keyword_names()
        seen = NormalizedDict(ignore="_")
        for name in names:
            try:
                kw = self._create_keyword(instance, name)
            except DataError as err:
                self._adding_keyword_failed(
                    name, err.message, err.details, self.getting_method_failed_level
                )
            else:
                if not kw:
                    continue
                try:
                    if kw.embedded:
                        self._validate_embedded(kw)
                    else:
                        self._handle_duplicates(kw, seen)
                except DataError as err:
                    self._adding_keyword_failed(kw.name, err.message, err.details)
                else:
                    keywords.append(kw)
                    library._logger.debug(f"Created keyword '{kw.name}'.")

    def _create_keyword(self, instance, name) -> "LibraryKeyword|None":
        raise NotImplementedError

    def _handle_duplicates(self, kw: LibraryKeyword, seen: NormalizedDict):
        if kw.name in seen:
            error = "Keyword with same name defined multiple times."
            seen[kw.name].error = error
            raise DataError(error)
        seen[kw.name] = kw

    def _validate_embedded(self, kw: LibraryKeyword):
        if len(kw.embedded.args) > kw.args.maxargs:
            raise DataError(
                "Keyword must accept at least as many positional arguments "
                "as it has embedded arguments."
            )
        if any(kw.embedded.types):
            arg, typ = next(
                (a, t) for a, t in zip(kw.embedded.args, kw.embedded.types) if t
            )
            raise DataError(
                f"Library keywords do not support type information with "
                f"embedded arguments like '${{{arg}: {typ}}}'. "
                f"Use type hints with function arguments instead."
            )
        kw.args.embedded = kw.embedded.args

    def _adding_keyword_failed(self, name, error, details, level="ERROR"):
        self.library.report_error(
            f"Adding keyword '{name}' failed: {error}",
            details,
            level=level,
            details_level="DEBUG",
        )


class StaticKeywordCreator(KeywordCreator):

    def __init__(
        self,
        library: TestLibrary,
        getting_method_failed_level="INFO",
        included_names=None,
        avoid_properties=False,
    ):
        super().__init__(library, getting_method_failed_level)
        self.included_names = included_names
        self.avoid_properties = avoid_properties

    def get_keyword_names(self) -> "list[str]":
        instance = self.library.instance
        try:
            return self._get_names(instance)
        except Exception:
            message, details = get_error_details()
            raise DataError(
                f"Getting keyword names from library '{self.library.name}' "
                f"failed: {message}",
                details,
            )

    def _get_names(self, instance) -> "list[str]":
        names = []
        auto_keywords = getattr(instance, "ROBOT_AUTO_KEYWORDS", True)
        included_names = self.included_names
        for name in dir(instance):
            if self._is_included(name, instance, auto_keywords, included_names):
                names.append(name)
        return names

    def _is_included(self, name, instance, auto_keywords, included_names) -> bool:
        if not (
            auto_keywords
            and name[:1] != "_"
            or self._is_explicitly_included(name, instance)
        ):
            return False
        return included_names is None or name in included_names

    def _is_explicitly_included(self, name, instance) -> bool:
        try:
            candidate = inspect.getattr_static(instance, name)
        except AttributeError:  # Attribute is dynamic. Try harder.
            try:
                candidate = getattr(instance, name)
            except Exception:  # Attribute is invalid. Report.
                msg, details = get_error_details()
                self._adding_keyword_failed(
                    name, msg, details, self.getting_method_failed_level
                )
                return False
        if isinstance(candidate, (classmethod, staticmethod)):
            candidate = candidate.__func__
        try:
            return hasattr(candidate, "robot_name")
        except Exception:
            return False

    def _create_keyword(self, instance, name) -> "StaticKeyword|None":
        if self.avoid_properties:
            self._pre_validate_method(instance, name)
        try:
            method = getattr(instance, name)
        except Exception:
            message, details = get_error_details()
            raise DataError(f"Getting handler method failed: {message}", details)
        self._validate_method(method)
        try:
            return StaticKeyword.from_name(name, self.library)
        except DataError as err:
            self._adding_keyword_failed(name, err.message, err.details)
        return None

    def _pre_validate_method(self, instance, name):
        try:
            candidate = inspect.getattr_static(instance, name)
        except AttributeError:  # Attribute is dynamic. Cannot pre-validate.
            return
        if isinstance(candidate, classmethod):
            candidate = candidate.__func__
        if isinstance(candidate, cached_property) or not inspect.isroutine(candidate):
            raise DataError("Not a method or function.")

    def _validate_method(self, candidate):
        if not (inspect.isroutine(candidate) or isinstance(candidate, partial)):
            raise DataError("Not a method or function.")
        if getattr(candidate, "robot_not_keyword", False):
            raise DataError("Not exposed as a keyword.")


class DynamicKeywordCreator(KeywordCreator):
    library: DynamicLibrary

    def __init__(self, library: "DynamicLibrary|HybridLibrary"):
        super().__init__(library, getting_method_failed_level="ERROR")

    def get_keyword_names(self) -> "list[str]":
        try:
            return GetKeywordNames(self.library.instance)()
        except DataError as err:
            raise DataError(
                f"Getting keyword names from library '{self.library.name}' "
                f"failed: {err}"
            )

    def _create_keyword(self, instance, name) -> DynamicKeyword:
        return DynamicKeyword.from_name(name, self.library)
