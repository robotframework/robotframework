#  Copyright 2008-2014 Nokia Solutions and Networks
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
from robot.variables import contains_var, is_list_var

from .arguments import (PythonArgumentParser, JavaArgumentParser,
                        DynamicArgumentParser, ArgumentResolver,
                        ArgumentMapper, JavaArgumentCoercer)
from .keywords import Keywords, Keyword
from .outputcapture import OutputCapturer
from .runkwregister import RUN_KW_REGISTER
from .signalhandler import STOP_SIGNAL_MONITOR




def Handler(library, name, method):
    if RUN_KW_REGISTER.is_run_keyword(library.orig_name, name):
        return _RunKeywordHandler(library, name, method)
    if utils.is_java_method(method):
        return _JavaHandler(library, name, method)
    else:
        return _PythonHandler(library, name, method)


def DynamicHandler(library, name, method, doc, argspec):
    if RUN_KW_REGISTER.is_run_keyword(library.orig_name, name):
        return _DynamicRunKeywordHandler(library, name, method, doc, argspec)
    return _DynamicHandler(library, name, method, doc, argspec)


def InitHandler(library, method, docgetter=None):
    Init = _PythonInitHandler if not utils.is_java_init(method) else _JavaInitHandler
    return Init(library, '__init__', method, docgetter)


class _RunnableHandler(object):
    type = 'library'
    _doc = ''
    _executed_in_dry_run = ('BuiltIn.Import Library',
                            'BuiltIn.Set Library Search Order')

    def __init__(self, library, handler_name, handler_method):
        self.library = library
        self.name = utils.printable_name(handler_name, code_style=True)
        self.arguments = self._parse_arguments(handler_method)
        self.pre_run_messages = None
        self._handler_name = handler_name
        self._method = self._get_initial_handler(library, handler_name,
                                                 handler_method)
        self._argument_resolver = self._get_argument_resolver(self.arguments)

    def _parse_arguments(self, handler_method):
        raise NotImplementedError

    def _get_argument_resolver(self, argspec):
        return ArgumentResolver(argspec)

    def _get_initial_handler(self, library, name, method):
        if library.scope == 'GLOBAL':
            return self._get_global_handler(method, name)
        return None

    def resolve_arguments(self, args, variables=None):
        return self._argument_resolver.resolve(args, variables)

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

    def init_keyword(self, varz):
        pass

    def run(self, context, args):
        if self.pre_run_messages:
            for message in self.pre_run_messages:
                context.output.message(message)
        if context.dry_run:
            return self._dry_run(context, args)
        return self._run(context, args)

    def _dry_run(self, context, args):
        if self.longname in self._executed_in_dry_run:
            return self._run(context, args)
        self.resolve_arguments(args)
        return None

    def _run(self, context, args):
        positional, named = \
            self.resolve_arguments(args, context.variables)
        context.output.trace(lambda: self._log_args(positional, named))
        runner = self._runner_for(self._current_handler(), context, positional,
                                  named, self._get_timeout(context))
        return self._run_with_output_captured_and_signal_monitor(runner, context)

    def _log_args(self, positional, named):
        positional = [utils.safe_repr(arg) for arg in positional]
        named = ['%s=%s' % (utils.unic(name), utils.safe_repr(value))
                 for name, value in named.items()]
        return 'Arguments: [ %s ]' % ' | '.join(positional + named)

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
            STOP_SIGNAL_MONITOR.start_running_keyword(context.in_teardown)
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

    def _get_timeout(self, context):
        timeouts = self._get_timeouts(context)
        return None if not timeouts else min(timeouts)

    def _get_timeouts(self, context):
        timeouts = [kw.timeout for kw in context.keywords]
        if context.test and not context.in_test_teardown:
            timeouts.append(context.test.timeout)
        return [timeout for timeout in timeouts if timeout]


class _PythonHandler(_RunnableHandler):

    def __init__(self, library, handler_name, handler_method):
        _RunnableHandler.__init__(self, library, handler_name, handler_method)
        self._doc = utils.getdoc(handler_method)

    def _parse_arguments(self, handler_method):
        return PythonArgumentParser().parse(handler_method, self.longname)


class _JavaHandler(_RunnableHandler):

    def __init__(self, library, handler_name, handler_method):
        _RunnableHandler.__init__(self, library, handler_name, handler_method)
        signatures = self._get_signatures(handler_method)
        self._arg_coercer = JavaArgumentCoercer(signatures, self.arguments)

    def _get_argument_resolver(self, argspec):
        return ArgumentResolver(argspec, dict_to_kwargs=True)

    def _parse_arguments(self, handler_method):
        signatures = self._get_signatures(handler_method)
        return JavaArgumentParser().parse(signatures, self.longname)

    def _get_signatures(self, handler):
        code_object = getattr(handler, 'im_func', handler)
        return code_object.argslist[:code_object.nargs]

    def resolve_arguments(self, args, variables=None):
        positional, named = self._argument_resolver.resolve(args, variables)
        arguments = self._arg_coercer.coerce(positional, named,
                                             dryrun=not variables)
        return arguments, {}


class _DynamicHandler(_RunnableHandler):

    def __init__(self, library, handler_name, dynamic_method, doc='',
                 argspec=None):
        self._argspec = argspec
        _RunnableHandler.__init__(self, library, handler_name,
                                  dynamic_method.method)
        self._run_keyword_method_name = dynamic_method.name
        self._doc = doc is not None and utils.unic(doc) or ''
        self._supports_kwargs = dynamic_method.supports_kwargs
        if argspec and argspec[-1].startswith('**'):
            if not self._supports_kwargs:
                raise DataError("Too few '%s' method parameters for **kwargs "
                                "support." % self._run_keyword_method_name)

    def _parse_arguments(self, handler_method):
        return DynamicArgumentParser().parse(self._argspec, self.longname)

    def resolve_arguments(self, arguments, variables=None):
        positional, named = _RunnableHandler.resolve_arguments(self, arguments, variables)
        mapper = ArgumentMapper(self.arguments)
        arguments, kwargs = mapper.map(positional, named, prune_trailing_defaults=True)
        return arguments, kwargs

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

    def __init__(self, library, handler_name, handler_method):
        _PythonHandler.__init__(self, library, handler_name, handler_method)
        self._handler_method = handler_method

    def _run_with_signal_monitoring(self, runner, context):
        # With run keyword variants, only the keyword to be run can fail
        # and therefore monitoring should not raise exception yet.
        return runner()

    def _get_argument_resolver(self, argspec):
        resolve_until = self._get_args_to_process()
        return ArgumentResolver(argspec, resolve_named=False,
                                resolve_variables_until=resolve_until)

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
            if contains_var(keyword.name):
                continue
            keywords.add_keyword(keyword)
        return keywords

    def _get_dry_run_keywords(self, args):
        if self._handler_name == 'run_keyword_if':
            return list(self._get_run_kw_if_keywords(args))
        if self._handler_name == 'run_keywords':
            return list(self._get_run_kws_keywords(args))
        if 'name' in self.arguments.positional and self._get_args_to_process() > 0:
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
        index = list(given_args).index(control_word)
        expr_and_call = given_args[:index]
        remaining = given_args[index+1:]
        if not (self._validate_kw_call(expr_and_call) and
                self._validate_kw_call(remaining, required_after)):
            raise DataError("Invalid 'Run Keyword If' usage.")
        if is_list_var(expr_and_call[0]):
            return (), remaining
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
                index = list(given_args).index('AND')
                kw_call, given_args = given_args[:index], given_args[index + 1:]
                yield kw_call
            if given_args:
                yield given_args

    def _get_default_run_kw_keywords(self, given_args):
        index = list(self.arguments.positional).index('name')
        return [Keyword(given_args[index], given_args[index+1:])]


class _XTimesHandler(_RunKeywordHandler):

    def __init__(self, handler, name):
        _RunKeywordHandler.__init__(self, handler.library, handler.name,
                                    handler._handler_method)
        self.name = name
        self._doc = "*DEPRECATED* Replace X times syntax with 'Repeat Keyword'."

    def run(self, context, args):
        resolved_times = context.namespace.variables.replace_string(self.name)
        _RunnableHandler.run(self, context, (resolved_times,) + tuple(args))

    @property
    def longname(self):
        return self.name


class _DynamicRunKeywordHandler(_DynamicHandler, _RunKeywordHandler):
    _parse_arguments = _RunKeywordHandler._parse_arguments
    _get_timeout = _RunKeywordHandler._get_timeout
    _get_argument_resolver = _RunKeywordHandler._get_argument_resolver


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
        parser = PythonArgumentParser(type='Test Library')
        return parser.parse(handler_method, self.library.name)


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
