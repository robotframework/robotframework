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
from typing import Any, Sequence

from robot.errors import DataError
from robot.libraries import STDLIBS
from robot.output import LOGGER
from robot.utils import (getdoc, get_error_details, Importer, is_dict_like, is_init,
                         is_list_like, normalize, NormalizedDict, seq2str2, type_name)

from .arguments import EmbeddedArguments, CustomArgumentConverters
from .dynamicmethods import (GetKeywordArguments, GetKeywordDocumentation,
                             GetKeywordNames, GetKeywordTags, RunKeyword)
from .handlers import Handler, InitHandler, DynamicHandler, EmbeddedArgumentsHandler
from .libraryscopes import Scope, ScopeManager
from .outputcapture import OutputCapturer
from .usererrorhandler import UserErrorHandler


class TestLibrary:
    # FIXME: Add docstrings and type hints! This is indirectly part of the public API.

    def __init__(self, code, *, name=None, real_name=None, source=None, logger=LOGGER):
        self.code = code
        self.name = name or code.__name__
        self.real_name = real_name or self.name
        self.source = source
        self.logger = logger
        self.init_args = ((), ())
        self._instance = None
        self.keywords = []
        self._has_listeners = None
        self.scope_manager = ScopeManager.for_library(self)

    @property
    def instance(self):
        instance = self.code if self._instance is None else self._instance
        if self._has_listeners is None:
            self._has_listeners = self._has_instance_listeners(instance)
        return instance

    @instance.setter
    def instance(self, instance):
        self._instance = instance

    @property
    def init(self):
        return InitHandler(self)

    @property
    def listeners(self):
        if self._has_listeners is None:
            self._has_listeners = self._has_instance_listeners(self.instance)
        if self._has_listeners is False:
            return []
        listener = self.instance.ROBOT_LIBRARY_LISTENER
        return list(listener) if is_list_like(listener) else [listener]

    def _has_instance_listeners(self, instance):
        return getattr(instance, 'ROBOT_LIBRARY_LISTENER', None) is not None

    @property
    def converters(self):
        converters = getattr(self.code, 'ROBOT_LIBRARY_CONVERTERS', None)
        if not converters:
            return None
        if not is_dict_like(converters):
            self.report_error(f'Argument converters must be given as a dictionary, '
                              f'got {type_name(converters)}.')
            return None
        return CustomArgumentConverters.from_dict(converters, self)

    @property
    def doc(self) -> str:
        return getdoc(self.instance)

    @property
    def doc_format(self) -> str:
        return self._attr('ROBOT_LIBRARY_DOC_FORMAT', upper=True)

    @property
    def scope(self) -> Scope:
        scope = self._attr('ROBOT_LIBRARY_SCOPE', 'TEST', upper=True)
        if scope == 'GLOBAL':
            return Scope.GLOBAL
        if scope in ('SUITE', 'TESTSUITE'):
            return Scope.SUITE
        return Scope.TEST

    @property
    def version(self) -> str:
        return self._attr('ROBOT_LIBRARY_VERSION') or self._attr('__version__')

    @property
    def lineno(self) -> int:
        return 1

    def _attr(self, name, default='', upper=False) -> str:
        value = str(getattr(self.code, name, default))
        if upper:
            value = normalize(value, ignore='_').upper()
        return value

    @classmethod
    def from_name(cls, name, *, real_name=None, args=None, variables=None,
                  create_keywords=True, logger=LOGGER):
        if name in STDLIBS:
            import_name = 'robot.libraries.' + name
        else:
            import_name = name
        if Path(name).exists():
            name = Path(name).stem
        with OutputCapturer(library_import=True):
            importer = Importer('library', logger=logger)
            code, source = importer.import_class_or_module(import_name,
                                                           return_source=True)
        return cls.from_code(code, name=name, real_name=real_name, source=source,
                             args=args, variables=variables,
                             create_keywords=create_keywords, logger=logger)

    @classmethod
    def from_code(cls, code, *, name=None, real_name=None, source=None, args=None,
                  variables=None, create_keywords=True, logger=LOGGER):
        if inspect.ismodule(code):
            lib = cls.from_module(code, name=name, real_name=real_name, source=source,
                                  create_keywords=create_keywords, logger=logger)
            if args:    # Resolving arguments reports an error.
                lib.init.resolve_arguments(args, variables)
            return lib
        return cls.from_class(code, name=name, real_name=real_name, source=source,
                              args=args or (), create_keywords=create_keywords,
                              variables=variables, logger=logger)

    @classmethod
    def from_module(cls, module, *, name=None, real_name=None, source=None,
                    create_keywords=True, logger=LOGGER):
        return ModuleLibrary.from_module(module, name=name, real_name=real_name,
                                         source=source, create_keywords=create_keywords,
                                         logger=logger)

    @classmethod
    def from_class(cls, klass, *, name=None, real_name=None, source=None, args=(),
                   create_keywords=True, variables=None, logger=LOGGER):
        if not GetKeywordNames(klass):
            library = ClassLibrary
        elif not RunKeyword(klass):
            library = HybridLibrary
        else:
            library = DynamicLibrary
        return library.from_class(klass, name=name, real_name=real_name, source=source,
                                  args=args, create_keywords=create_keywords,
                                  variables=variables, logger=logger)

    def create_keywords(self):
        raise NotImplementedError

    def find_keywords(self, name: str,
                      include_embedded: bool = True) -> 'list[LibraryKeyword]':
        # FIXME: This is duplication from ResourceFile. Move to some common place?
        # FIXME: This is also rather slow.
        keywords = []
        norm_name = normalize(name, ignore='_')
        for kw in self.keywords:
            if kw.embedded:
                if include_embedded and kw.matches(name):
                    keywords.append(kw)
            else:
                if normalize(kw.name, ignore='_') == norm_name:
                    keywords.append(kw)
        return keywords

    def report_error(self, message, details=None, level='ERROR', details_level='INFO'):
        prefix = 'Error in' if level in ('ERROR', 'WARN') else 'In'
        self.logger.write(f"{prefix} library '{self.name}': {message}", level)
        if details:
            self.logger.write(f'Details:\n{details}', details_level)


class ModuleLibrary(TestLibrary):

    @property
    def scope(self) -> Scope:
        return Scope.GLOBAL

    @classmethod
    def from_module(cls, module, *, name=None, real_name=None, source=None,
                    create_keywords=True, logger=LOGGER):
        library = cls(module, name=name, source=source, real_name=real_name,
                      logger=logger)
        if create_keywords:
            library.create_keywords()
        return library

    @classmethod
    def from_class(cls, *args, **kws):
        raise TypeError(f"Cannot create '{cls.__name__}' from class.")

    def create_keywords(self):
        excludes = getattr(self.code, '__all__', None)
        StaticKeywordCreator(self, excluded_names=excludes).create_keywords()


class ClassLibrary(TestLibrary):

    def __init__(self, code, *, name=None, real_name=None, source=None,
                 positional_args: Sequence[Any] = (),
                 named_args: 'Sequence[tuple[Any, Any]]' = (), logger=LOGGER):
        super().__init__(code, name=name, real_name=real_name, source=source, logger=logger)
        self.init_args = (positional_args, named_args)
        self.instance = None

    @property
    def init(self):
        init = getattr(self.code, '__init__', None)
        return InitHandler(self, init if is_init(init) else None)

    @property
    def instance(self):
        if self._instance is None:
            positional, named = self.init_args
            try:
                with OutputCapturer(library_import=True):
                    self._instance = self.code(*positional, **dict(named))
            except Exception:
                message, details = get_error_details()
                if positional or named:
                    args = seq2str2([str(p) for p in positional] +
                                    [f'{name}={value}' for name, value in named])
                    args_text = f'arguments {args}'
                else:
                    args_text = 'no arguments'
                raise DataError(f"Initializing library '{self.name}' with {args_text} failed: "
                                f"{message}\n{details}")
        if self._has_listeners is None:
            self._has_listeners = self._has_instance_listeners(self._instance)
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
            if line.strip().startswith('class '):
                return start_lineno + increment
        return start_lineno

    @classmethod
    def from_module(cls, *args, **kws):
        raise TypeError(f"Cannot create '{cls.__name__}' from module.")

    @classmethod
    def from_class(cls, klass, *, name=None, real_name=None, source=None, args=(),
                   create_keywords=True, variables=None, logger=LOGGER):
        library = cls(klass, name=name, real_name=real_name, source=source, logger=logger)
        positional, named = library.init.resolve_arguments(args, variables)
        library.init_args = (tuple(positional), tuple(named))
        if create_keywords:
            library.create_keywords()
        return library

    def create_keywords(self):
        StaticKeywordCreator(self, avoid_propertys=True).create_keywords()


class HybridLibrary(ClassLibrary):

    def create_keywords(self):
        names = DynamicKeywordCreator(self).get_keyword_names()
        creator = StaticKeywordCreator(self, getting_method_failed_level='ERROR')
        creator.create_keywords(names)


class DynamicLibrary(ClassLibrary):

    @property
    def init(self):
        init = super().init
        init.doc_getter = lambda: GetKeywordDocumentation(self.instance)('__init__')
        return init

    @property
    def doc(self) -> str:
        return GetKeywordDocumentation(self.instance)('__intro__') or super().doc

    def create_keywords(self):
        DynamicKeywordCreator(self).create_keywords()


class KeywordCreator:

    def __init__(self, library: TestLibrary):
        self.library = library

    def get_keyword_names(self):
        raise NotImplementedError

    def create_keywords(self, names=None):
        library = self.library
        library.keywords = keywords = []
        if names is None:
            names = self.get_keyword_names()
        seen = NormalizedDict(ignore='_')
        for name in names:
            kw = self._create_keyword(library.instance, name, seen)
            if kw:
                keywords.append(kw)
                library.logger.debug(f"Created keyword '{kw.name}'.")

    def _create_keyword(self, instance, name, seen):
        try:
            keyword = self._create_normal_keyword(instance, name)
        except DataError as err:
            self._adding_keyword_failed(name, err)
            return None
        embedded = EmbeddedArguments.from_name(keyword.name) if keyword else None
        if embedded:
            try:
                keyword = self._create_embedded_args_keyword(keyword, embedded)
            except DataError as err:
                self._adding_keyword_failed(keyword.name, err)
                return None
        return self._handle_duplicates(keyword, seen)

    def _create_normal_keyword(self, instance, name):
        raise NotImplementedError

    def _create_embedded_args_keyword(self, keyword, embedded):
        if len(embedded.args) > keyword.arguments.maxargs:
            raise DataError(f'Keyword must accept at least as many positional '
                            f'arguments as it has embedded arguments.')
        keyword.arguments.embedded = embedded.args
        return EmbeddedArgumentsHandler(embedded, keyword)

    def _adding_keyword_failed(self, name, error, level='ERROR'):
        self.library.report_error(
            f"Adding keyword '{name}' failed: {error}",
            error.details,
            level=level,
            details_level='DEBUG'
        )

    def _handle_duplicates(self, kw, seen: NormalizedDict):
        if not kw or kw.embedded:
            return kw
        if kw.name not in seen:
            seen[kw.name] = kw
            return kw
        error = DataError('Keyword with same name defined multiple times.')
        kw = UserErrorHandler(error, kw.name, kw.owner)
        index = self.library.keywords.index(seen[kw.name])
        self.library.keywords[index] = seen[kw.name] = kw
        self._adding_keyword_failed(kw.name, error)
        return None


class StaticKeywordCreator(KeywordCreator):

    def __init__(self, library: TestLibrary, *, excluded_names=None,
                 avoid_propertys=False,
                 getting_method_failed_level='INFO'):
        super().__init__(library)
        self.excluded_names = excluded_names
        self.avoid_propertys = avoid_propertys
        self.getting_method_failed_level = getting_method_failed_level

    def get_keyword_names(self):
        instance = self.library.instance
        try:
            return self._get_names(instance)
        except Exception:
            message, details = get_error_details()
            raise DataError(f"Getting keyword names from library '{self.library.name}' "
                            f"failed: {message}", details)

    def _get_names(self, instance) -> 'list[str]':
        def explicitly_included(name):
            candidate = inspect.getattr_static(instance, name)
            if isinstance(candidate, (classmethod, staticmethod)):
                candidate = candidate.__func__
            try:
                return hasattr(candidate, 'robot_name')
            except Exception:
                return False

        names = []
        auto_keywords = getattr(instance, 'ROBOT_AUTO_KEYWORDS', True)
        excluded_names = self.excluded_names
        for name in dir(instance):
            if not auto_keywords:
                if not explicitly_included(name):
                    continue
            elif name[:1] == '_':
                if not explicitly_included(name):
                    continue
            elif excluded_names is not None:
                if name not in excluded_names:
                    continue
            names.append(name)
        return names

    def _create_normal_keyword(self, instance, name):
        try:
            method = self._get_method(instance, name)
        except DataError as err:
            self._adding_keyword_failed(name, err, self.getting_method_failed_level)
            return None
        else:
            return Handler(self.library, name, method)

    def _get_method(self, instance, name):
        if self.avoid_propertys:
            candidate = inspect.getattr_static(instance, name)
            self._pre_validate_method(candidate)
        try:
            method = getattr(instance, name)
        except Exception:
            message, details = get_error_details()
            raise DataError(f'Getting handler method failed: {message}', details)
        self._validate_method(method)
        return method

    def _pre_validate_method(self, candidate):
        if isinstance(candidate, classmethod):
            candidate = candidate.__func__
        if isinstance(candidate, cached_property) or not inspect.isroutine(candidate):
            raise DataError('Not a method or function.')

    def _validate_method(self, candidate):
        if not (inspect.isroutine(candidate) or isinstance(candidate, partial)):
            raise DataError('Not a method or function.')
        if getattr(candidate, 'robot_not_keyword', False):
            raise DataError('Not exposed as a keyword.')


class DynamicKeywordCreator(KeywordCreator):

    def get_keyword_names(self):
        try:
            return GetKeywordNames(self.library.instance)()
        except DataError as err:
            raise DataError(f"Getting keyword names from library '{self.library.name}' "
                            f"failed: {err}")

    def _create_normal_keyword(self, instance, name):
        args = GetKeywordArguments(instance)(name)
        tags = GetKeywordTags(instance)(name)
        doc = GetKeywordDocumentation(instance)(name)
        method = RunKeyword(instance)
        return DynamicHandler(self.library, name, method, doc, args, tags)
