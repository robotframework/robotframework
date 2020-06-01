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

from copy import copy
import inspect

from robot.utils import (getdoc, getshortdoc, is_java_init, is_java_method,
                         is_list_like, normpath, printable_name,
                         split_tags_from_doc, type_name, unwrap)
from robot.errors import DataError
from robot.model import Tags

from .arguments import (ArgumentSpec, DynamicArgumentParser,
                        JavaArgumentCoercer, JavaArgumentParser,
                        PythonArgumentParser)
from .dynamicmethods import GetKeywordSource, GetKeywordTypes
from .librarykeywordrunner import (EmbeddedArgumentsRunner,
                                   LibraryKeywordRunner, RunKeywordRunner)
from .runkwregister import RUN_KW_REGISTER


def Handler(library, name, method):
    if RUN_KW_REGISTER.is_run_keyword(library.orig_name, name):
        return _RunKeywordHandler(library, name, method)
    if is_java_method(method):
        return _JavaHandler(library, name, method)
    else:
        return _PythonHandler(library, name, method)


def DynamicHandler(library, name, method, doc, argspec, tags=None):
    if RUN_KW_REGISTER.is_run_keyword(library.orig_name, name):
        return _DynamicRunKeywordHandler(library, name, method, doc, argspec, tags)
    return _DynamicHandler(library, name, method, doc, argspec, tags)


def InitHandler(library, method=None, docgetter=None):
    Init = _PythonInitHandler if not is_java_init(method) else _JavaInitHandler
    return Init(library, '__init__', method, docgetter)


class _RunnableHandler(object):

    def __init__(self, library, handler_name, handler_method, doc='', tags=None):
        self.library = library
        self._handler_name = handler_name
        self.name = self._get_name(handler_name, handler_method)
        self.arguments = self._parse_arguments(handler_method)
        self._method = self._get_initial_handler(library, handler_name,
                                                 handler_method)
        doc, tags_from_doc = split_tags_from_doc(doc or '')
        tags_from_attr = self._get_tags_from_attribute(handler_method)
        self._doc = doc
        self.tags = Tags(tuple(tags_from_doc) +
                         tuple(tags_from_attr) +
                         tuple(tags or ()))

    def _get_name(self, handler_name, handler_method):
        robot_name = getattr(handler_method, 'robot_name', None)
        name = robot_name or printable_name(handler_name, code_style=True)
        if not name:
            raise DataError('Keyword name cannot be empty.')
        return name

    def _parse_arguments(self, handler_method):
        raise NotImplementedError

    def _get_tags_from_attribute(self, handler_method):
        tags = getattr(handler_method, 'robot_tags', ())
        if not is_list_like(tags):
            raise DataError("Expected tags to be list-like, got %s."
                            % type_name(tags))
        return tags

    def _get_initial_handler(self, library, name, method):
        if library.scope.is_global:
            return self._get_global_handler(method, name)
        return None

    def resolve_arguments(self, args, variables=None):
        return self.arguments.resolve(args, variables)

    @property
    def doc(self):
        return self._doc

    @property
    def longname(self):
        return '%s.%s' % (self.library.name, self.name)

    @property
    def shortdoc(self):
        return getshortdoc(self.doc)

    @property
    def libname(self):
        return self.library.name

    @property
    def source(self):
        return self.library.source

    @property
    def lineno(self):
        return -1

    def create_runner(self, name):
        return LibraryKeywordRunner(self)

    def current_handler(self):
        if self._method:
            return self._method
        return self._get_handler(self.library.get_instance(), self._handler_name)

    def _get_global_handler(self, method, name):
        return method

    def _get_handler(self, lib_instance, handler_name):
        try:
            return getattr(lib_instance, handler_name)
        except AttributeError:
            # Occurs with old-style classes.
            if handler_name == '__init__':
                return None
            raise


class _PythonHandler(_RunnableHandler):

    def __init__(self, library, handler_name, handler_method):
        _RunnableHandler.__init__(self, library, handler_name, handler_method,
                                  getdoc(handler_method))

    def _parse_arguments(self, handler_method):
        return PythonArgumentParser().parse(handler_method, self.longname)

    @property
    def source(self):
        handler = self.current_handler()
        # `getsourcefile` can return None and raise TypeError.
        try:
            source = inspect.getsourcefile(unwrap(handler))
        except TypeError:
            source = None
        return normpath(source) if source else self.library.source

    @property
    def lineno(self):
        handler = self.current_handler()
        try:
            lines, start_lineno = inspect.getsourcelines(unwrap(handler))
        except (TypeError, OSError, IOError):
            return -1
        for increment, line in enumerate(lines):
            if line.strip().startswith('def '):
                return start_lineno + increment
        return start_lineno


class _JavaHandler(_RunnableHandler):

    def __init__(self, library, handler_name, handler_method):
        _RunnableHandler.__init__(self, library, handler_name, handler_method)
        signatures = self._get_signatures(handler_method)
        self._arg_coercer = JavaArgumentCoercer(signatures, self.arguments)

    def _parse_arguments(self, handler_method):
        signatures = self._get_signatures(handler_method)
        return JavaArgumentParser().parse(signatures, self.longname)

    def _get_signatures(self, handler):
        code_object = getattr(handler, 'im_func', handler)
        return code_object.argslist[:code_object.nargs]

    def resolve_arguments(self, args, variables=None):
        positional, named = self.arguments.resolve(args, variables,
                                                   dict_to_kwargs=True)
        arguments = self._arg_coercer.coerce(positional, named,
                                             dryrun=not variables)
        return arguments, []


class _DynamicHandler(_RunnableHandler):

    def __init__(self, library, handler_name, dynamic_method, doc='',
                 argspec=None, tags=None):
        self._argspec = argspec
        self._run_keyword_method_name = dynamic_method.name
        self._supports_kwargs = dynamic_method.supports_kwargs
        _RunnableHandler.__init__(self, library, handler_name,
                                  dynamic_method.method, doc, tags)
        self._source_info = None

    def _parse_arguments(self, handler_method):
        spec = DynamicArgumentParser().parse(self._argspec, self.longname)
        if not self._supports_kwargs:
            if spec.kwargs:
                raise DataError("Too few '%s' method parameters for **kwargs "
                                "support." % self._run_keyword_method_name)
            if spec.kwonlyargs:
                raise DataError("Too few '%s' method parameters for "
                                "keyword-only arguments support."
                                % self._run_keyword_method_name)
        get_keyword_types = GetKeywordTypes(self.library.get_instance())
        spec.types = get_keyword_types(self._handler_name)
        return spec

    @property
    def source(self):
        if self._source_info is None:
            self._source_info = self._get_source_info()
        return self._source_info[0]

    def _get_source_info(self):
        get_keyword_source = GetKeywordSource(self.library.get_instance())
        try:
            source = get_keyword_source(self._handler_name)
        except DataError as err:
            self.library.report_error(
                "Getting source information for keyword '%s' failed: %s"
                % (self.name, err.message), err.details
            )
            return None, -1
        if not source:
            return self.library.source, -1
        if ':' not in source:
            return source, -1
        path, lineno = source.rsplit(':', 1)
        try:
            return path or self.library.source, int(lineno)
        except ValueError:
            return source, -1

    @property
    def lineno(self):
        if self._source_info is None:
            self._source_info = self._get_source_info()
        return self._source_info[1]

    def resolve_arguments(self, arguments, variables=None):
        positional, named = self.arguments.resolve(arguments, variables)
        if not self._supports_kwargs:
            positional, named = self.arguments.map(positional, named)
        return positional, named

    def _get_handler(self, lib_instance, handler_name):
        runner = getattr(lib_instance, self._run_keyword_method_name)
        return self._get_dynamic_handler(runner, handler_name)

    def _get_global_handler(self, method, name):
        return self._get_dynamic_handler(method, name)

    def _get_dynamic_handler(self, runner, name):
        def handler(*positional, **kwargs):
            if self._supports_kwargs:
                return runner(name, positional, kwargs)
            else:
                return runner(name, positional)
        return handler


class _RunKeywordHandler(_PythonHandler):

    def create_runner(self, name):
        default_dry_run_keywords = ('name' in self.arguments.positional and
                                    self._args_to_process)
        return RunKeywordRunner(self, default_dry_run_keywords)

    @property
    def _args_to_process(self):
        return RUN_KW_REGISTER.get_args_to_process(self.library.orig_name,
                                                   self.name)

    def resolve_arguments(self, args, variables=None):
        args_to_process = self._args_to_process
        return self.arguments.resolve(args, variables, resolve_named=False,
                                      resolve_variables_until=args_to_process)


class _DynamicRunKeywordHandler(_DynamicHandler, _RunKeywordHandler):
    _parse_arguments = _RunKeywordHandler._parse_arguments
    resolve_arguments = _RunKeywordHandler.resolve_arguments


class _PythonInitHandler(_PythonHandler):

    def __init__(self, library, handler_name, handler_method, docgetter):
        _PythonHandler.__init__(self, library, handler_name, handler_method)
        self._docgetter = docgetter

    @property
    def doc(self):
        if self._docgetter:
            self._doc = self._docgetter() or self._doc
            self._docgetter = None
        return self._doc

    def _parse_arguments(self, init_method):
        parser = PythonArgumentParser(type='Test Library')
        return parser.parse(init_method or (lambda: None), self.library.name)


class _JavaInitHandler(_JavaHandler):

    def __init__(self, library, handler_name, handler_method, docgetter):
        _JavaHandler.__init__(self, library, handler_name, handler_method)
        self._docgetter = docgetter

    @property
    def doc(self):
        if self._docgetter:
            self._doc = self._docgetter() or self._doc
            self._docgetter = None
        return self._doc

    def _parse_arguments(self, handler_method):
        parser = JavaArgumentParser(type='Test Library')
        signatures = self._get_signatures(handler_method)
        return parser.parse(signatures, self.library.name)


class EmbeddedArgumentsHandler(object):

    def __init__(self, name_regexp, orig_handler):
        self.arguments = ArgumentSpec()  # Show empty argument spec for Libdoc
        self.name_regexp = name_regexp
        self._orig_handler = orig_handler

    def __getattr__(self, item):
        return getattr(self._orig_handler, item)

    @property
    def library(self):
        return self._orig_handler.library

    @library.setter
    def library(self, library):
        self._orig_handler.library = library

    def matches(self, name):
        return self.name_regexp.match(name) is not None

    def create_runner(self, name):
        return EmbeddedArgumentsRunner(self, name)

    def __copy__(self):
        orig_handler = copy(self._orig_handler)
        return EmbeddedArgumentsHandler(self.name_regexp, orig_handler)
