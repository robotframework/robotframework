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

from itertools import chain

from robot.errors import (BreakLoop, ContinueLoop, DataError, ExecutionFailed,
                          ExecutionPassed, ExecutionStatus, PassExecution,
                          ReturnFromKeyword, UserKeywordExecutionFailed, VariableError)
from robot.result import Keyword as KeywordResult
from robot.utils import DotDict, getshortdoc, prepr, split_tags_from_doc
from robot.variables import is_list_variable, VariableAssignment

from .arguments import DefaultValue
from .bodyrunner import BodyRunner, KeywordRunner
from .statusreporter import StatusReporter
from .timeouts import KeywordTimeout


class UserKeywordRunner:

    def __init__(self, handler, name=None):
        self._handler = handler
        self.name = name or handler.name
        self.pre_run_messages = ()

    @property
    def longname(self):
        libname = self._handler.libname
        return f'{libname}.{self.name}' if libname else self.name

    @property
    def libname(self):
        return self._handler.libname

    @property
    def tags(self):
        return self._handler.tags

    @property
    def source(self):
        return self._handler.source

    @property
    def arguments(self):
        """:rtype: :py:class:`robot.running.arguments.ArgumentSpec`"""
        return self._handler.arguments

    def run(self, kw, context, run=True):
        assignment = VariableAssignment(kw.assign)
        result = self._get_result(kw, assignment, context.variables)
        with StatusReporter(kw, result, context, run):
            if self._handler.private:
                context.warn_on_invalid_private_call(self._handler)
            with assignment.assigner(context) as assigner:
                if run:
                    return_value = self._run(context, kw.args, result)
                    assigner.assign(return_value)
                    return return_value

    def _get_result(self, kw, assignment, variables):
        handler = self._handler
        doc = variables.replace_string(handler.doc, ignore_errors=True)
        doc, tags = split_tags_from_doc(doc)
        tags = variables.replace_list(handler.tags, ignore_errors=True) + tags
        return KeywordResult(kwname=self.name,
                             libname=handler.libname,
                             doc=getshortdoc(doc),
                             args=kw.args,
                             assign=tuple(assignment),
                             tags=tags,
                             type=kw.type)

    def _run(self, context, args, result):
        if self.pre_run_messages:
            for message in self.pre_run_messages:
                context.output.message(message)
        variables = context.variables
        args = self._resolve_arguments(args, variables)
        with context.user_keyword(self._handler):
            self._set_arguments(args, context)
            timeout = self._get_timeout(variables)
            if timeout is not None:
                result.timeout = str(timeout)
            with context.timeout(timeout):
                exception, return_ = self._execute(context)
                if exception and not exception.can_continue(context):
                    raise exception
                return_value = self._get_return_value(variables, return_)
                if exception:
                    exception.return_value = return_value
                    raise exception
                return return_value

    def _get_timeout(self, variables=None):
        timeout = self._handler.timeout
        return KeywordTimeout(timeout, variables) if timeout else None

    def _resolve_arguments(self, arguments, variables=None):
        return self.arguments.resolve(arguments, variables)

    def _set_arguments(self, arguments, context):
        positional, named = arguments
        variables = context.variables
        args, kwargs = self.arguments.map(positional, named,
                                          replace_defaults=False)
        self._set_variables(args, kwargs, variables)
        context.output.trace(lambda: self._trace_log_args_message(variables),
                             write_if_flat=False)

    def _set_variables(self, positional, kwargs, variables):
        spec = self.arguments
        args, varargs = self._split_args_and_varargs(positional)
        kwonly, kwargs = self._split_kwonly_and_kwargs(kwargs)
        for name, value in chain(zip(spec.positional, args), kwonly):
            if isinstance(value, DefaultValue):
                value = value.resolve(variables)
            variables[f'${{{name}}}'] = value
        if spec.var_positional:
            variables[f'@{{{spec.var_positional}}}'] = varargs
        if spec.var_named:
            variables[f'&{{{spec.var_named}}}'] = DotDict(kwargs)

    def _split_args_and_varargs(self, args):
        if not self.arguments.var_positional:
            return args, []
        positional = len(self.arguments.positional)
        return args[:positional], args[positional:]

    def _split_kwonly_and_kwargs(self, all_kwargs):
        kwonly = []
        kwargs = []
        for name, value in all_kwargs:
            target = kwonly if name in self.arguments.named_only else kwargs
            target.append((name, value))
        return kwonly, kwargs

    def _trace_log_args_message(self, variables):
        return self._format_trace_log_args_message(
            self._format_args_for_trace_logging(), variables)

    def _format_args_for_trace_logging(self):
        args = [f'${{{arg}}}' for arg in self.arguments.positional]
        if self.arguments.var_positional:
            args.append(f'@{{{self.arguments.var_positional}}}')
        if self.arguments.var_named:
            args.append(f'&{{{self.arguments.var_named}}}')
        return args

    def _format_trace_log_args_message(self, args, variables):
        args = ' | '.join(f'{name}={prepr(variables[name])}' for name in args)
        return f'Arguments: [ {args} ]'

    def _execute(self, context):
        handler = self._handler
        if context.dry_run and handler.tags.robot('no-dry-run'):
            return None, None
        error = return_ = pass_ = None
        try:
            BodyRunner(context).run(handler.body)
        except ReturnFromKeyword as exception:
            return_ = exception
            error = exception.earlier_failures
        except (BreakLoop, ContinueLoop) as exception:
            pass_ = exception
        except ExecutionPassed as exception:
            pass_ = exception
            error = exception.earlier_failures
            if error:
                error.continue_on_failure = False
        except ExecutionFailed as exception:
            error = exception
        if handler.teardown:
            with context.keyword_teardown(error):
                td_error = self._run_teardown(handler.teardown, context)
        else:
            td_error = None
        if error or td_error:
            error = UserKeywordExecutionFailed(error, td_error)
        return error or pass_, return_

    def _get_return_value(self, variables, return_):
        ret = self._handler.return_value if not return_ else return_.return_value
        if not ret:
            return None
        contains_list_var = any(is_list_variable(item) for item in ret)
        try:
            ret = variables.replace_list(ret)
        except DataError as err:
            raise VariableError(f'Replacing variables from keyword return '
                                f'value failed: {err}')
        if len(ret) != 1 or contains_list_var:
            return ret
        return ret[0]

    def _run_teardown(self, teardown, context):
        try:
            name = context.variables.replace_string(teardown.name)
        except DataError as err:
            if context.dry_run:
                return None
            return ExecutionFailed(err.message, syntax=True)
        if name.upper() in ('', 'NONE'):
            return None
        try:
            KeywordRunner(context).run(teardown, name)
        except PassExecution:
            return None
        except ExecutionStatus as err:
            return err
        return None

    def dry_run(self, kw, context):
        assignment = VariableAssignment(kw.assign)
        result = self._get_result(kw, assignment, context.variables)
        with StatusReporter(kw, result, context):
            assignment.validate_assignment()
            self._dry_run(context, kw.args, result)

    def _dry_run(self, context, args, result):
        if self.pre_run_messages:
            for message in self.pre_run_messages:
                context.output.message(message)
        self._resolve_arguments(args)
        with context.user_keyword(self._handler):
            timeout = self._get_timeout()
            if timeout:
                result.timeout = str(timeout)
            error, _ = self._execute(context)
            if error:
                raise error


class EmbeddedArgumentsRunner(UserKeywordRunner):

    def __init__(self, handler, name):
        super().__init__(handler, name)
        self.embedded_args = handler.embedded.match(name).groups()

    def _resolve_arguments(self, args, variables=None):
        self.arguments.resolve(args, variables)
        if variables:
            embedded = [variables.replace_scalar(e) for e in self.embedded_args]
            self.embedded_args = self._handler.embedded.map(embedded)
        return super()._resolve_arguments(args, variables)

    def _set_arguments(self, args, context):
        variables = context.variables
        for name, value in self.embedded_args:
            variables[f'${{{name}}}'] = value
        super()._set_arguments(args, context)
        context.output.trace(lambda: self._trace_log_args_message(variables),
                             write_if_flat=False)

    def _trace_log_args_message(self, variables):
        args = [f'${{{arg}}}' for arg in self._handler.embedded.args]
        args += self._format_args_for_trace_logging()
        return self._format_trace_log_args_message(args, variables)

    def _get_result(self, kw, assignment, variables):
        result = UserKeywordRunner._get_result(self, kw, assignment, variables)
        result.sourcename = self._handler.name
        return result
