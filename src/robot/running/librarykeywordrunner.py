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

from robot.errors import DataError
from robot.output import LOGGER
from robot.result import Keyword as KeywordResult
from robot.utils import prepr, unic
from robot.variables import contains_variable, is_list_variable, VariableAssignment

from .bodyrunner import BodyRunner
from .model import Keyword
from .outputcapture import OutputCapturer
from .signalhandler import STOP_SIGNAL_MONITOR
from .statusreporter import StatusReporter


class LibraryKeywordRunner(object):

    def __init__(self, handler, name=None):
        self._handler = handler
        self.name = name or handler.name
        self.pre_run_messages = None

    @property
    def library(self):
        return self._handler.library

    @property
    def libname(self):
        return self._handler.library.name

    @property
    def longname(self):
        return '%s.%s' % (self.library.name, self.name)

    def run(self, kw, context, run=True):
        assignment = VariableAssignment(kw.assign)
        result = self._get_result(kw, assignment)
        with StatusReporter(kw, result, context, run):
            if run:
                with assignment.assigner(context) as assigner:
                    return_value = self._run(context, kw.args)
                    assigner.assign(return_value)
                    return return_value

    def _get_result(self, kw, assignment):
        handler = self._handler
        return KeywordResult(kwname=self.name,
                             libname=handler.libname,
                             doc=handler.shortdoc,
                             args=kw.args,
                             assign=tuple(assignment),
                             tags=handler.tags,
                             type=kw.type)

    def _run(self, context, args):
        if self.pre_run_messages:
            for message in self.pre_run_messages:
                context.output.message(message)
        variables = context.variables if not context.dry_run else None
        positional, named = self._handler.resolve_arguments(args, variables)
        context.output.trace(lambda: self._trace_log_args(positional, named))
        runner = self._runner_for(context, self._handler.current_handler(),
                                  positional, dict(named))
        return self._run_with_output_captured_and_signal_monitor(runner, context)

    def _trace_log_args(self, positional, named):
        args = [prepr(arg) for arg in positional]
        args += ['%s=%s' % (unic(n), prepr(v)) for n, v in named]
        return 'Arguments: [ %s ]' % ' | '.join(args)

    def _runner_for(self, context, handler, positional, named):
        timeout = self._get_timeout(context)
        if timeout and timeout.active:
            def runner():
                with LOGGER.delayed_logging:
                    context.output.debug(timeout.get_message)
                    return timeout.run(handler, args=positional, kwargs=named)
            return runner
        return lambda: handler(*positional, **named)

    def _get_timeout(self, context):
        return min(context.timeouts) if context.timeouts else None

    def _run_with_output_captured_and_signal_monitor(self, runner, context):
        with OutputCapturer():
            return self._run_with_signal_monitoring(runner, context)

    def _run_with_signal_monitoring(self, runner, context):
        try:
            STOP_SIGNAL_MONITOR.start_running_keyword(context.in_teardown)
            return runner()
        finally:
            STOP_SIGNAL_MONITOR.stop_running_keyword()

    def dry_run(self, kw, context):
        assignment = VariableAssignment(kw.assign)
        result = self._get_result(kw, assignment)
        with StatusReporter(kw, result, context, run=False):
            assignment.validate_assignment()
            self._dry_run(context, kw.args)

    def _dry_run(self, context, args):
        if self._executed_in_dry_run(self._handler):
            self._run(context, args)
        else:
            self._handler.resolve_arguments(args)

    def _executed_in_dry_run(self, handler):
        keywords_to_execute = ('BuiltIn.Import Library',
                               'BuiltIn.Set Library Search Order',
                               'BuiltIn.Set Tags',
                               'BuiltIn.Remove Tags')
        return (handler.libname == 'Reserved' or
                handler.longname in keywords_to_execute)


class EmbeddedArgumentsRunner(LibraryKeywordRunner):

    def __init__(self, handler, name):
        LibraryKeywordRunner.__init__(self, handler, name)
        self._embedded_args = handler.name_regexp.match(name).groups()

    def _run(self, context, args):
        if args:
            raise DataError("Positional arguments are not allowed when using "
                            "embedded arguments.")
        return LibraryKeywordRunner._run(self, context, self._embedded_args)

    def _dry_run(self, context, args):
        return LibraryKeywordRunner._dry_run(self, context, self._embedded_args)

    def _get_result(self, kw, assignment):
        result = LibraryKeywordRunner._get_result(self, kw, assignment)
        result.sourcename = self._handler.name
        return result


class RunKeywordRunner(LibraryKeywordRunner):

    def __init__(self, handler, default_dry_run_keywords=False):
        LibraryKeywordRunner.__init__(self, handler)
        self._default_dry_run_keywords = default_dry_run_keywords

    def _get_timeout(self, context):
        return None

    def _run_with_output_captured_and_signal_monitor(self, runner, context):
        return self._run_with_signal_monitoring(runner, context)

    def _dry_run(self, context, args):
        LibraryKeywordRunner._dry_run(self, context, args)
        keywords = [kw for kw in self._get_dry_run_keywords(args)
                    if not contains_variable(kw.name)]
        BodyRunner(context).run(keywords)

    def _get_dry_run_keywords(self, args):
        name = self._handler.name
        if name == 'Run Keyword If':
            return self._get_run_kw_if_keywords(args)
        if name == 'Run Keywords':
            return self._get_run_kws_keywords(args)
        if self._default_dry_run_keywords:
            return self._get_default_run_kw_keywords(args)
        return []

    def _get_run_kw_if_keywords(self, given_args):
        for kw_call in self._get_run_kw_if_calls(given_args):
            if kw_call:
                yield Keyword(name=kw_call[0], args=kw_call[1:])

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
            if not is_list_variable(expr):
                yield kw_call

    def _split_run_kw_if_args(self, given_args, control_word, required_after):
        index = list(given_args).index(control_word)
        expr_and_call = given_args[:index]
        remaining = given_args[index+1:]
        if not (self._validate_kw_call(expr_and_call) and
                    self._validate_kw_call(remaining, required_after)):
            raise DataError("Invalid 'Run Keyword If' usage.")
        if is_list_variable(expr_and_call[0]):
            return (), remaining
        return expr_and_call[1:], remaining

    def _validate_kw_call(self, kw_call, min_length=2):
        if len(kw_call) >= min_length:
            return True
        return any(is_list_variable(item) for item in kw_call)

    def _get_run_kws_keywords(self, given_args):
        for kw_call in self._get_run_kws_calls(given_args):
            yield Keyword(name=kw_call[0], args=kw_call[1:])

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
        index = list(self._handler.arguments.positional).index('name')
        return [Keyword(name=given_args[index], args=given_args[index+1:])]
