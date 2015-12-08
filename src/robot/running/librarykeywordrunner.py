#  Copyright 2008-2015 Nokia Solutions and Networks
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

from robot.errors import DataError, ExecutionFailed, HandlerExecutionFailed
from robot.model import Keywords
from robot.result.keyword import Keyword as KeywordResult
from robot.utils import ErrorDetails, prepr, unic
from robot.variables import VariableAssigner, contains_var, is_list_var

from .keywordrunner import KeywordRunner, StatusReporter, SyntaxErrorReporter
from .model import Keyword
from .outputcapture import OutputCapturer
from .signalhandler import STOP_SIGNAL_MONITOR


# FIXME: cleanup helper method names
class LibraryKeywordRunner(object):
    _executed_in_dry_run = ('BuiltIn.Import Library',
                            'BuiltIn.Set Library Search Order')

    def __init__(self, handler):
        self._handler = handler

    def run(self, kw, context):
        assigner = VariableAssigner(kw.assign)
        handler = self._handler
        result = KeywordResult(kwname=handler.name or '',
                               libname=handler.libname or '',
                               doc=handler.shortdoc,
                               args=kw.args,
                               assign=assigner.assignment,
                               tags=handler.tags,
                               type=kw.type)
        with StatusReporter(context, result, context.dry_run):
            self._warn_if_deprecated(result.name, result.doc, context)
            return self._run_and_assign(context, kw.args, assigner)

    def _warn_if_deprecated(self, name, doc, context):
        if doc.startswith('*DEPRECATED') and '*' in doc[1:]:
            message = ' ' + doc.split('*', 2)[-1].strip()
            context.warn("Keyword '%s' is deprecated.%s" % (name, message))

    def _run_and_assign(self, context, args, assigner):
        syntax_error_reporter = SyntaxErrorReporter(context)
        with syntax_error_reporter:
            assigner.validate_assignment()
        return_value, exception = self._run(context, args)
        if not exception or exception.can_continue(context.in_teardown):
            with syntax_error_reporter:
                assigner.assign(context, return_value)
        if exception:
            raise exception
        return return_value

    def _run(self, context, args):
        return_value = exception = None
        try:
            if not context.dry_run:
                return_value = self._handler_run(context, args)
            else:
                return_value = self._handler_dry_run(context, args)
        except ExecutionFailed as err:
            exception = err
        except:
            exception = self._get_and_report_failure(context)
        if exception:
            return_value = exception.return_value
        return return_value, exception

    def _get_and_report_failure(self, context):
        failure = HandlerExecutionFailed(ErrorDetails())
        if failure.timeout:
            context.timeout_occurred = True
        context.fail(failure.full_message)
        if failure.traceback:
            context.debug(failure.traceback)
        return failure

    def _handler_dry_run(self, context, args):
        if self._handler.longname in self._executed_in_dry_run:
            return self._handler_run(context, args)
        self._handler.resolve_arguments(args)
        return None

    def _handler_run(self, context, args):
        if self._handler.pre_run_messages:
            for message in self._handler.pre_run_messages:
                context.output.message(message)
        positional, named = \
            self._handler.resolve_arguments(args, context.variables)
        context.output.trace(lambda: self._log_args(positional, named))
        runner = self._runner_for(self._handler.current_handler(), context, positional,
                                  dict(named), self._get_timeout(context))
        return self._run_with_output_captured_and_signal_monitor(runner, context)

    def _log_args(self, positional, named):
        positional = [prepr(arg) for arg in positional]
        named = ['%s=%s' % (unic(name), prepr(value))
                 for name, value in named]
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

    def _get_timeout(self, context):
        return min(context.timeouts) if context.timeouts else None


class EmbeddedArgumentsRunner(LibraryKeywordRunner):

    def _handler_run(self, context, args):
        if args:
            raise DataError("Positional arguments are not allowed when using "
                            "embedded arguments.")
        return LibraryKeywordRunner._handler_run(self, context,
                                                 self._handler._embedded_args)


class RunKeywordRunner(LibraryKeywordRunner):

    # TODO: Should this be removed altogether?
    # - Doesn't seem to be really needed.
    # - Not used with dynamic run kws in the new design (at least currently)
    def _get_timeout(self, namespace):
        return None

    def _run_with_output_captured_and_signal_monitor(self, runner, context):
        return self._run_with_signal_monitoring(runner, context)

    def _handler_dry_run(self, context, args):
        LibraryKeywordRunner._handler_dry_run(self, context, args)
        keywords = self._get_runnable_dry_run_keywords(args)
        KeywordRunner(context).run_keywords(keywords)

    def _get_runnable_dry_run_keywords(self, args):
        keywords = Keywords()
        for keyword in self._get_dry_run_keywords(args):
            if contains_var(keyword.name):
                continue
            keywords.append(keyword)
        return keywords

    def _get_dry_run_keywords(self, args):
        # FIXME: _handler._handler_name is fugly. Pass handler_name to __init__?
        if self._handler._handler_name == 'run_keyword_if':
            return list(self._get_run_kw_if_keywords(args))
        if self._handler._handler_name == 'run_keywords':
            return list(self._get_run_kws_keywords(args))
        if 'name' in self._handler.arguments.positional and self._handler._get_args_to_process() > 0:
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
