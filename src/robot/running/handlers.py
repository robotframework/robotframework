#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

from __future__ import with_statement

from robot import utils
from robot.errors import DataError
from robot.variables import is_list_var

from .arguments import (PythonKeywordArguments, JavaKeywordArguments,
                        DynamicKeywordArguments, RunKeywordArguments,
                        PythonInitArguments, JavaInitArguments)
from .keywords import Keywords, Keyword
from .outputcapture import OutputCapturer
from .runkwregister import RUN_KW_REGISTER
from .signalhandler import STOP_SIGNAL_MONITOR


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


def InitHandler(library, method, docgetter=None):
    Init = _PythonInitHandler if not _is_java_init(method) else _JavaInitHandler
    return Init(library, '__init__', method, docgetter)


class _BaseHandler(object):
    type = 'library'
    _doc = ''

    def __init__(self, library, handler_name, handler_method):
        self.library = library
        self.name = utils.printable_name(handler_name, code_style=True)
        self.arguments = self._parse_arguments(handler_method)

    def _parse_arguments(self, handler_method):
        raise NotImplementedError(self.__class__.__name__)

    @property
    def doc(self):
        return self._doc

    @property
    def longname(self):
        return '%s.%s' % (self.library.name, self.name)

    @property
    def shortdoc(self):
        return self.doc.splitlines()[0] if self.doc else ''

    @property
    def libname(self):
        return self.library.name


class _RunnableHandler(_BaseHandler):

    def __init__(self, library, handler_name, handler_method):
        _BaseHandler.__init__(self, library, handler_name, handler_method)
        self._handler_name = handler_name
        self._method = self._get_initial_handler(library, handler_name,
                                                 handler_method)

    def _get_initial_handler(self, library, name, method):
        if library.scope == 'GLOBAL':
            return self._get_global_handler(method, name)
        return None

    def init_keyword(self, varz):
        pass

    def run(self, context, args):
        if context.dry_run:
            return self._dry_run(context, args)
        return self._run(context, args)

    def _dry_run(self, context, args):
        if self.longname == 'BuiltIn.Import Library':
            return self._run(context, args)
        self.arguments.check_arg_limits_for_dry_run(args)
        return None

    def _run(self, context, args):
        positional, named = \
            self.arguments.resolve(args, context.get_current_vars())
        self.arguments.trace_log_args(context.output, positional, named)
        runner = self._runner_for(self._current_handler(), context, positional,
                                  named, self._get_timeout(context.namespace))
        return self._run_with_output_captured_and_signal_monitor(runner, context)

    def _runner_for(self, handler, context, positional, named, timeout):
        if timeout and timeout.active:
            context.output.debug(timeout.get_message)
            return lambda: timeout.run(handler, args=positional, kwargs=named)
        return lambda: handler(*positional, **named)

    def _run_with_output_captured_and_signal_monitor(self, runner, context):
        with OutputCapturer():
            return self._run_with_signal_monitoring(runner, context)

    def _run_with_signal_monitoring(self, runner, context):
        try:
            STOP_SIGNAL_MONITOR.start_running_keyword(context.teardown)
            return runner()
        finally:
            STOP_SIGNAL_MONITOR.stop_running_keyword()

    def _current_handler(self):
        if self._method:
            return self._method
        return self._get_handler(self.library.get_instance(), self._handler_name)

    def _get_global_handler(self, method, name):
        return method

    def _get_handler(self, lib_instance, handler_name):
        return getattr(lib_instance, handler_name)

    def _get_timeout(self, namespace):
        timeoutable = self._get_timeoutable_items(namespace)
        if timeoutable:
            return min(item.timeout for item in timeoutable)
        return None

    def _get_timeoutable_items(self, namespace):
        items = namespace.uk_handlers[:]
        if self._test_running_and_not_in_teardown(namespace.test):
            items.append(namespace.test)
        return items

    def _test_running_and_not_in_teardown(self, test):
        return test and test.status == 'RUNNING'


class _PythonHandler(_RunnableHandler):

    def __init__(self, library, handler_name, handler_method):
        _RunnableHandler.__init__(self, library, handler_name, handler_method)
        self._doc = utils.getdoc(handler_method)

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
        self._doc = doc is not None and utils.unic(doc) or ''

    def _parse_arguments(self, handler_method):
        return DynamicKeywordArguments(self._argspec, self.longname)

    def _get_handler(self, lib_instance, handler_name):
        runner = getattr(lib_instance, self._run_keyword_method_name)
        return self._get_dynamic_handler(runner, handler_name)

    def _separate_to_positional_and_kw_args(self, arguments):
        def reducer(collector, value):
            if '=' in value:
                collector[1].append(value.split('='))
            else:
                collector[0] = collector[0] + 1
            return collector
        return reduce(reducer, arguments, [0, []])

    def _get_global_handler(self, method, name):
        return self._get_dynamic_handler(method, name)

    def _get_dynamic_handler(self, runner, name):
        def handler(*args, **kwargs):
            kw_arguments = []
            kwargs = kwargs.copy()
            if self._argspec:
                number_of_positionals, keyword_arguments = self._separate_to_positional_and_kw_args(self._argspec)
                skip = len(args) - number_of_positionals
                for named_argument, default_value in keyword_arguments[skip:skip + 1]:
                    if named_argument in kwargs:
                        kw_arguments.append(kwargs[named_argument])
                        kwargs.pop(named_argument)
                    else:
                        kw_arguments.append(default_value)
            return runner(name, list(args) + kw_arguments + kwargs.values())
        return handler


class _RunKeywordHandler(_PythonHandler):

    def __init__(self, library, handler_name, handler_method):
        _PythonHandler.__init__(self, library, handler_name, handler_method)
        self._handler_method = handler_method

    def _run_with_signal_monitoring(self, runner, context):
        # With run keyword variants, only the keyword to be run can fail
        # and therefore monitoring should not raise exception yet.
        return runner()

    def _parse_arguments(self, handler_method):
        arg_index = self._get_args_to_process()
        return RunKeywordArguments(handler_method, self.longname, arg_index)

    def _get_args_to_process(self):
        return RUN_KW_REGISTER.get_args_to_process(self.library.orig_name,
                                                   self.name)

    def _get_timeout(self, namespace):
        return None

    def _dry_run(self, context, args):
        _RunnableHandler._dry_run(self, context, args)
        keywords = self._get_runnable_dry_run_keywords(context, args)
        keywords.run(context)

    def _get_runnable_dry_run_keywords(self, context, args):
        keywords = Keywords([])
        for keyword in self._get_dry_run_keywords(args):
            if self._variable_syntax_in(keyword.name, context):
                continue
            keywords.add_keyword(keyword)
        return keywords

    def _variable_syntax_in(self, kw_name, context):
        try:
            resolved = context.namespace.variables.replace_string(kw_name)
            #Variable can contain value, but it might be wrong,
            #therefore it cannot be returned
            return resolved != kw_name
        except DataError:
            return True

    def _get_dry_run_keywords(self, args):
        if self._handler_name == 'run_keyword_if':
            return list(self._get_run_kw_if_keywords(args))
        if self._handler_name == 'run_keywords':
            return list(self._get_run_kws_keywords(args))
        if 'name' in self.arguments.names and self._get_args_to_process() > 0:
            return self._get_default_run_kw_keywords(args)
        return []

    def _get_run_kw_if_keywords(self, given_args):
        for kw_call in self._get_run_kw_if_calls(given_args):
            if kw_call:
                yield Keyword(kw_call[0], kw_call[1:])

    def _get_run_kw_if_calls(self, given_args):
        while 'ELSE IF' in given_args:
            kw_call, given_args = self._split_run_kw_if_args(given_args, 'ELSE IF', 2)
            yield kw_call
        if 'ELSE' in given_args:
            kw_call, else_call = self._split_run_kw_if_args(given_args, 'ELSE', 1)
            yield kw_call
            yield else_call
        elif self._validate_kw_call(given_args):
            expr, kw_call = given_args[0], given_args[1:]
            if not is_list_var(expr):
                yield kw_call

    def _split_run_kw_if_args(self, given_args, control_word, required_after):
        index = given_args.index(control_word)
        expr_and_call = given_args[:index]
        remaining = given_args[index+1:]
        if not (self._validate_kw_call(expr_and_call) and
                self._validate_kw_call(remaining, required_after)):
            raise DataError("Invalid 'Run Keyword If' usage.")
        if is_list_var(expr_and_call[0]):
            return [], remaining
        return expr_and_call[1:], remaining

    def _validate_kw_call(self, kw_call, min_length=2):
        if len(kw_call) >= min_length:
            return True
        return any(is_list_var(item) for item in kw_call)

    def _get_run_kws_keywords(self, given_args):
        for kw_call in self._get_run_kws_calls(given_args):
            yield Keyword(kw_call[0], kw_call[1:])

    def _get_run_kws_calls(self, given_args):
        if 'AND' not in given_args:
            for kw_call in given_args:
                yield [kw_call,]
        else:
            while 'AND' in given_args:
                index = given_args.index('AND')
                kw_call, given_args = given_args[:index], given_args[index + 1:]
                yield kw_call
            if given_args:
                yield given_args

    def _get_default_run_kw_keywords(self, given_args):
        index = self.arguments.names.index('name')
        return [Keyword(given_args[index], given_args[index+1:])]


class _XTimesHandler(_RunKeywordHandler):

    def __init__(self, handler, name):
        _RunKeywordHandler.__init__(self, handler.library, handler.name,
                                    handler._handler_method)
        self.name = name
        self._doc = "*DEPRECATED* Replace X times syntax with 'Repeat Keyword'."

    def run(self, context, args):
        resolved_times = context.namespace.variables.replace_string(self.name)
        _RunnableHandler.run(self, context, [resolved_times] + args)

    @property
    def longname(self):
        return self.name


class _DynamicRunKeywordHandler(_DynamicHandler, _RunKeywordHandler):
    _parse_arguments = _RunKeywordHandler._parse_arguments
    _get_timeout = _RunKeywordHandler._get_timeout


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

    def _parse_arguments(self, handler_method):
        return PythonInitArguments(handler_method, self.library.name)


class _JavaInitHandler(_BaseHandler):

    def __init__(self, library, handler_name, handler_method, docgetter):
        _BaseHandler.__init__(self, library, handler_name, handler_method)
        self._docgetter = docgetter

    @property
    def doc(self):
        if self._docgetter:
            self._doc = self._docgetter() or self._doc
            self._docgetter = None
        return self._doc

    def _parse_arguments(self, handler_method):
        return JavaInitArguments(handler_method, self.library.name)
