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

from contextlib import contextmanager
from typing import TYPE_CHECKING

from robot.errors import DataError
from robot.output import LOGGER
from robot.result import Keyword as KeywordResult
from robot.utils import prepr, safe_str
from robot.variables import contains_variable, is_list_variable, VariableAssignment

from .bodyrunner import BodyRunner
from .model import Keyword as KeywordData
from .resourcemodel import UserKeyword
from .outputcapture import OutputCapturer
from .signalhandler import STOP_SIGNAL_MONITOR
from .statusreporter import StatusReporter

if TYPE_CHECKING:
    from .librarykeyword import LibraryKeyword


class LibraryKeywordRunner:

    def __init__(self, keyword: 'LibraryKeyword', name: 'str|None' = None,
                 languages=None):
        self.keyword = keyword
        self.name = name or keyword.name
        self.pre_run_messages = ()
        self.languages = languages

    def run(self, data: KeywordData, result: KeywordResult, context, run=True):
        kw = self.keyword.bind(data)
        assignment = VariableAssignment(data.assign)
        self._config_result(result, data, kw, assignment)
        with StatusReporter(data, result, context, run, implementation=kw):
            if run:
                with assignment.assigner(context) as assigner:
                    return_value = self._run(data, kw, context)
                    assigner.assign(return_value)
                    return return_value

    def _config_result(self, result: KeywordResult, data: KeywordData,
                       kw: 'LibraryKeyword', assignment):
        args = tuple(data.args)
        if data.named_args:
            args += tuple(f'{n}={v}' for n, v in data.named_args.items())
        result.config(name=self.name,
                      owner=kw.owner.name,
                      doc=kw.short_doc,
                      args=args,
                      assign=tuple(assignment),
                      tags=kw.tags,
                      type=data.type)

    def _run(self, data: KeywordData, kw: 'LibraryKeyword', context):
        if self.pre_run_messages:
            for message in self.pre_run_messages:
                context.output.message(message)
        variables = context.variables if not context.dry_run else None
        positional, named = self._resolve_arguments(data, kw, variables)
        context.output.trace(lambda: self._trace_log_args(positional, named),
                             write_if_flat=False)
        if kw.error:
            raise DataError(kw.error)
        return self._execute(kw.method, positional, named, context)

    def _resolve_arguments(self, data: KeywordData, kw: 'LibraryKeyword', variables=None):
        return kw.resolve_arguments(data.args, data.named_args, variables, self.languages)

    def _trace_log_args(self, positional, named):
        args = [prepr(arg) for arg in positional]
        args += ['%s=%s' % (safe_str(n), prepr(v)) for n, v in named]
        return 'Arguments: [ %s ]' % ' | '.join(args)

    def _runner_for(self, method, positional, named, context):
        timeout = self._get_timeout(context)
        if timeout and timeout.active:
            def runner():
                with LOGGER.delayed_logging:
                    context.output.debug(timeout.get_message)
                    return timeout.run(method, args=positional, kwargs=named)
            return runner
        return lambda: method(*positional, **named)

    def _get_timeout(self, context):
        return min(context.timeouts) if context.timeouts else None

    def _execute(self, method, positional, named, context):
        timeout = self._get_timeout(context)
        if timeout and timeout.active:
            method = self._wrap_with_timeout(method, timeout, context.output)
        with self._monitor(context):
            result = method(*positional, **dict(named))
            if context.asynchronous.is_loop_required(result):
                return context.asynchronous.run_until_complete(result)
            return result

    def _wrap_with_timeout(self, method, timeout, output):
        def wrapper(*args, **kwargs):
            with output.delayed_logging:
                output.debug(timeout.get_message)
                return timeout.run(method, args=args, kwargs=kwargs)
        return wrapper

    @contextmanager
    def _monitor(self, context):
        STOP_SIGNAL_MONITOR.start_running_keyword(context.in_teardown)
        capturer = OutputCapturer()
        capturer.start()
        try:
            yield
        finally:
            capturer.stop()
            STOP_SIGNAL_MONITOR.stop_running_keyword()

    def dry_run(self, data: KeywordData, result: KeywordResult, context):
        kw = self.keyword.bind(data)
        assignment = VariableAssignment(data.assign)
        self._config_result(result, data, kw, assignment)
        with StatusReporter(data, result, context, run=False, implementation=kw):
            assignment.validate_assignment()
            if self._executed_in_dry_run(kw):
                self._run(data, kw, context)
            else:
                self._resolve_arguments(data, kw)
            self._end_dry_run(data, kw, result, context)

    def _end_dry_run(self, data: KeywordData, kw: 'LibraryKeyword',
                     result: KeywordResult, context):
        pass

    def _executed_in_dry_run(self, kw: 'LibraryKeyword'):
        return (kw.owner.name == 'BuiltIn'
                and kw.name in ('Import Library', 'Set Library Search Order',
                                'Set Tags', 'Remove Tags', 'Import Resource'))


class EmbeddedArgumentsRunner(LibraryKeywordRunner):

    def __init__(self, keyword: 'LibraryKeyword', name: 'str'):
        super().__init__(keyword, name)
        self.embedded_args = keyword.embedded.match(name).groups()

    def _resolve_arguments(self, data: KeywordData, kw: 'LibraryKeyword', variables=None):
        return kw.resolve_arguments(self.embedded_args + data.args, data.named_args,
                                    variables, self.languages)

    def _config_result(self, result: KeywordResult, data: KeywordData,
                       kw: 'LibraryKeyword', assignment):
        super()._config_result(result, data, kw, assignment)
        result.source_name = kw.name


class RunKeywordRunner(LibraryKeywordRunner):

    def __init__(self, keyword: 'LibraryKeyword', execute_in_dry_run=False):
        super().__init__(keyword)
        self.execute_in_dry_run = execute_in_dry_run

    def _get_timeout(self, context):
        # These keywords are not affected by timeouts. Keywords they execute are.
        return None

    @contextmanager
    def _monitor(self, context):
        STOP_SIGNAL_MONITOR.start_running_keyword(context.in_teardown)
        try:
            yield
        finally:
            STOP_SIGNAL_MONITOR.stop_running_keyword()

    def _end_dry_run(self, data: KeywordData, kw: 'LibraryKeyword',
                     result: KeywordResult, context):
        wrapper = UserKeyword(name=kw.name,
                              doc="Wraps keywords executed by '{kw.name}' in dry-run.",
                              parent=kw.parent)
        wrapper.body = [k for k in self._get_dry_run_keywords(kw, data.args)
                        if not contains_variable(k.name)]
        BodyRunner(context).run(wrapper, result)

    def _get_dry_run_keywords(self, kw: 'LibraryKeyword', args):
        if not self.execute_in_dry_run:
            return []
        if kw.name == 'Run Keyword If':
            return self._get_dry_run_keywords_for_run_keyword_if(args)
        if kw.name == 'Run Keywords':
            return self._get_dry_run_keywords_for_run_keyword(args)
        return self._get_dry_run_keywords_based_on_name(kw, args)

    def _get_dry_run_keywords_for_run_keyword_if(self, given_args):
        for kw_call in self._get_run_kw_if_calls(given_args):
            if kw_call:
                yield KeywordData(name=kw_call[0], args=kw_call[1:])

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

    def _get_dry_run_keywords_for_run_keyword(self, given_args):
        for kw_call in self._get_run_kws_calls(given_args):
            yield KeywordData(name=kw_call[0], args=kw_call[1:])

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

    def _get_dry_run_keywords_based_on_name(self, kw: 'LibraryKeyword', given_args):
        index = kw.args.positional.index('name')
        return [KeywordData(name=given_args[index], args=given_args[index+1:])]
