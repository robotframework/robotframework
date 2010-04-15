#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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

from robot import utils

from runkwregister import RUN_KW_REGISTER
from arguments import PythonKeywordArguments, JavaKeywordArguments, \
    DynamicKeywordArguments, PythonInitArguments, JavaInitArguments, \
    RunKeywordArguments


if utils.is_jython:
    from org.python.core import PyReflectedFunction, PyReflectedConstructor

    def _is_java_init(init):
        return isinstance(init, PyReflectedConstructor)
    def _is_java_method(method):
        return hasattr(method, 'im_func') \
               and isinstance(method.im_func, PyReflectedFunction)
else:
    _is_java_init = _is_java_method = lambda item: False


def Handler(library, name, method):
    if RUN_KW_REGISTER.is_run_keyword(library.orig_name, name):
        return _RunKeywordHandler(library, name, method)
    if _is_java_method(method):
        return _JavaHandler(library, name, method)
    else:
        return _PythonHandler(library, name, method)


def DynamicHandler(library, name, method, doc, argspec):
    if RUN_KW_REGISTER.is_run_keyword(library.orig_name, name):
        return _DynamicRunKeywordHandler(library, name, method, doc, argspec)
    return _DynamicHandler(library, name, method, doc, argspec)


def InitHandler(library, method):
    if method is None:
        method = lambda: None
    Init = _PythonInitHandler if not _is_java_init(method) else _JavaInitHandler
    return Init(library, '__init__', method)


class _BaseHandler(object):
    type = 'library'
    longname = property(lambda self: '%s.%s' % (self.library.name, self.name))
    shortdoc = property(lambda self: self.doc.splitlines()[0] if self.doc else '')

    def __init__(self, library, handler_name, handler_method):
        self.library = library
        self.name = utils.printable_name(handler_name, code_style=True)
        self.arguments = self._parse_arguments(handler_method)

    def _parse_arguments(self, handler_method):
        raise NotImplementedError(self.__class__.__name__)


class _RunnableHandler(_BaseHandler):

    def __init__(self, library, handler_name, handler_method):
        _BaseHandler.__init__(self, library, handler_name, handler_method)
        self._handler_name = handler_name
        self._method = self._get_global_handler(handler_method, handler_name) \
            if library.scope == 'GLOBAL' else None
        self.doc = ''

    def run(self, output, namespace, args):
        self._capture_output()
        posargs, kwargs = self.arguments.resolve(args, namespace.variables,
                                                 output)
        try:
            return self._run_handler(self._current_handler(), output, posargs,
                                     kwargs, self._get_timeout(namespace))
        finally:
            self._release_and_log_output(output)

    def _run_handler(self, handler, output, posargs, kwargs, timeout):
        if timeout is not None and timeout.active():
            return timeout.run(handler, args=posargs, kwargs=kwargs, logger=output)
        return handler(*posargs, **kwargs)

    def _capture_output(self):
        utils.capture_output()

    def _release_and_log_output(self, logger):
        stdout, stderr = utils.release_output()
        logger.log_output(stdout)
        logger.log_output(stderr)
        if stderr.strip() != '':
            sys.stderr.write(stderr+'\n')

    def _current_handler(self):
        if self._method is not None:
            return self._method
        return self._get_handler(self.library.get_instance(),
                                 self._handler_name)

    def _get_global_handler(self, method, name):
        return method

    def _get_handler(self, lib_instance, handler_name):
        return getattr(lib_instance, handler_name)

    def _get_timeout(self, namespace):
        timeoutable = self._get_timeoutable_items(namespace)
        if len(timeoutable) > 0 :
            return min([ item.timeout for item in timeoutable ])
        return None

    def _get_timeoutable_items(self, namespace):
        items = namespace.uk_handlers[:]
        if namespace.test is not None and namespace.test.status == 'RUNNING':
            items.append(namespace.test)
        return items


class _PythonHandler(_RunnableHandler):

    def __init__(self, library, handler_name, handler_method):
        _RunnableHandler.__init__(self, library, handler_name, handler_method)
        self.doc = utils.get_doc(handler_method)

    def _parse_arguments(self, handler_method):
        return PythonKeywordArguments(handler_method, self.longname)


class _JavaHandler(_RunnableHandler):

    def _parse_arguments(self, handler_method):
        return JavaKeywordArguments(handler_method, self.longname)


class _DynamicHandler(_RunnableHandler):

    def __init__(self, library, handler_name, handler_method, doc='',
                 argspec=None):
        self._argspec = argspec
        _RunnableHandler.__init__(self, library, handler_name, handler_method)
        self._run_keyword_method_name = handler_method.__name__
        self.doc = doc is not None and utils.unic(doc) or ''

    def _parse_arguments(self, handler_method):
        return DynamicKeywordArguments(self._argspec, self.longname)

    def _get_handler(self, lib_instance, handler_name):
        runner = getattr(lib_instance, self._run_keyword_method_name)
        return self._get_dynamic_handler(runner, handler_name)

    def _get_global_handler(self, method, name):
        return self._get_dynamic_handler(method, name)

    def _get_dynamic_handler(self, runner, name):
        def handler(*args):
            return runner(name, list(args))
        return handler


class _RunKeywordHandler(_PythonHandler):

    def _parse_arguments(self, handler_method):
        arg_index = RUN_KW_REGISTER.get_args_to_process(self.library.orig_name,
                                                        self.name)
        return RunKeywordArguments(handler_method, self.longname, arg_index)

    def _get_timeout(self, namespace):
        return None


class _DynamicRunKeywordHandler(_DynamicHandler, _RunKeywordHandler):
    _parse_arguments = _RunKeywordHandler._parse_arguments
    _get_timeout = _RunKeywordHandler._get_timeout


class _PythonInitHandler(_BaseHandler):

    def _parse_arguments(self, handler_method):
        return PythonInitArguments(handler_method, self.library.name)


class _JavaInitHandler(_BaseHandler):

    def _parse_arguments(self, handler_method):
        return JavaInitArguments(handler_method, self.library.name)
