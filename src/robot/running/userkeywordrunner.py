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

from robot.errors import (DataError, ExecutionFailed, ExecutionPassed, ExecutionStatus,
                          PassExecution, ReturnFromKeyword, UserKeywordExecutionFailed,
                          VariableError)
from robot.result import Keyword as KeywordResult
from robot.utils import DotDict, getshortdoc, prepr, split_tags_from_doc
from robot.variables import is_list_variable, VariableAssignment

from .arguments import DefaultValue
from .bodyrunner import BodyRunner, KeywordRunner
from .statusreporter import StatusReporter
from .timeouts import KeywordTimeout


class UserKeywordRunner:

    def __init__(self, keyword, name=None):
        self.keyword = keyword
        self.name = name or keyword.name
        self.pre_run_messages = ()

    # FIXME: UserKeywordRunner shouldn't need the following propertys.
    # Code needing them should use UserKeyword directly.

    @property
    def full_name(self):
        owner = self.keyword.owner
        return f'{owner.name}.{self.name}' if owner and owner.name else self.name

    @property
    def tags(self):
        return self.keyword.tags

    @property
    def source(self):
        return self.keyword.source

    @property
    def error(self):
        return self.keyword.error

    @property
    def arguments(self):
        """:rtype: :py:class:`robot.running.arguments.ArgumentSpec`"""
        return self.keyword.args

    def run(self, data, context, run=True):
        kw = self.keyword.bind(data)
        assignment = VariableAssignment(data.assign)
        result = self._get_result(kw, data, assignment, context.variables)
        with StatusReporter(data, result, context, run, implementation=kw):
            if kw.private:
                context.warn_on_invalid_private_call(kw)
            with assignment.assigner(context) as assigner:
                if run:
                    return_value = self._run(kw, data.args, result, context)
                    assigner.assign(return_value)
                    return return_value

    def _get_result(self, kw, data, assignment, variables):
        doc = variables.replace_string(kw.doc, ignore_errors=True)
        doc, tags = split_tags_from_doc(doc)
        tags = variables.replace_list(kw.tags, ignore_errors=True) + tags
        return KeywordResult(name=self.name,
                             owner=kw.owner.name,
                             doc=getshortdoc(doc),
                             args=data.args,
                             assign=tuple(assignment),
                             tags=tags,
                             type=data.type)

    def _run(self, kw, args, result, context):
        if self.pre_run_messages:
            for message in self.pre_run_messages:
                context.output.message(message)
        variables = context.variables
        args = self._resolve_arguments(kw, args, variables)
        with context.user_keyword(kw):
            self._set_arguments(kw, args, context)
            if kw.timeout:
                timeout = KeywordTimeout(kw.timeout, variables)
                result.timeout = str(timeout)
            else:
                timeout = None
            with context.timeout(timeout):
                exception, return_value = self._execute(kw, context)
                if exception and not exception.can_continue(context):
                    raise exception
                return_value = self._handle_return_value(return_value, variables)
                if exception:
                    exception.return_value = return_value
                    raise exception
                return return_value

    def _resolve_arguments(self, kw, args, variables=None):
        return kw.args.resolve(args, variables)

    def _set_arguments(self, kw, args, context):
        positional, named = args
        variables = context.variables
        args, kwargs = kw.args.map(positional, named, replace_defaults=False)
        self._set_variables(kw.args, args, kwargs, variables)
        context.output.trace(lambda: self._trace_log_args_message(kw, variables),
                             write_if_flat=False)

    def _set_variables(self, spec, positional, kwargs, variables):
        args, varargs = self._split_args_and_varargs(spec, positional)
        kwonly, kwargs = self._split_kwonly_and_kwargs(spec, kwargs)
        for name, value in chain(zip(spec.positional, args), kwonly):
            if isinstance(value, DefaultValue):
                value = value.resolve(variables)
            variables[f'${{{name}}}'] = value
        if spec.var_positional:
            variables[f'@{{{spec.var_positional}}}'] = varargs
        if spec.var_named:
            variables[f'&{{{spec.var_named}}}'] = DotDict(kwargs)

    def _split_args_and_varargs(self, spec, args):
        if not spec.var_positional:
            return args, []
        positional = len(spec.positional)
        return args[:positional], args[positional:]

    def _split_kwonly_and_kwargs(self, spec, all_kwargs):
        kwonly = []
        kwargs = []
        for name, value in all_kwargs:
            target = kwonly if name in spec.named_only else kwargs
            target.append((name, value))
        return kwonly, kwargs

    def _trace_log_args_message(self, kw, variables):
        return self._format_trace_log_args_message(
            self._format_args_for_trace_logging(kw.args), variables
        )

    def _format_args_for_trace_logging(self, spec):
        args = [f'${{{arg}}}' for arg in spec.positional]
        if spec.var_positional:
            args.append(f'@{{{spec.var_positional}}}')
        if spec.var_named:
            args.append(f'&{{{spec.var_named}}}')
        return args

    def _format_trace_log_args_message(self, args, variables):
        args = ' | '.join(f'{name}={prepr(variables[name])}' for name in args)
        return f'Arguments: [ {args} ]'

    def _execute(self, kw, context):
        if kw.error:
            raise DataError(kw.error)
        if not kw.body:
            raise DataError('User keyword cannot be empty.')
        if not kw.name:
            raise DataError('User keyword name cannot be empty.')
        if context.dry_run and kw.tags.robot('no-dry-run'):
            return None, None
        error = success = return_value = None
        if kw.setup:
            error = self._run_setup_or_teardown(kw.setup, context)
        try:
            BodyRunner(context, run=not error).run(kw.body)
        except ReturnFromKeyword as exception:
            return_value = exception.return_value
            error = exception.earlier_failures
        except ExecutionPassed as exception:
            success = exception
            error = exception.earlier_failures
            if error:
                error.continue_on_failure = False
        except ExecutionFailed as exception:
            error = exception
        if kw.teardown:
            with context.keyword_teardown(error):
                td_error = self._run_setup_or_teardown(kw.teardown, context)
        else:
            td_error = None
        if error or td_error:
            error = UserKeywordExecutionFailed(error, td_error)
        return error or success, return_value

    def _handle_return_value(self, return_value, variables):
        if not return_value:
            return None
        contains_list_var = any(is_list_variable(item) for item in return_value)
        try:
            return_value = variables.replace_list(return_value)
        except DataError as err:
            raise VariableError(f'Replacing variables from keyword return '
                                f'value failed: {err}')
        if len(return_value) != 1 or contains_list_var:
            return return_value
        return return_value[0]

    def _run_setup_or_teardown(self, item, context):
        try:
            name = context.variables.replace_string(item.name)
        except DataError as err:
            if context.dry_run:
                return None
            return ExecutionFailed(err.message, syntax=True)
        if name.upper() in ('', 'NONE'):
            return None
        try:
            KeywordRunner(context).run(item, name)
        except PassExecution:
            return None
        except ExecutionStatus as err:
            return err
        return None

    def dry_run(self, data, context):
        kw = self.keyword.bind(data)
        assignment = VariableAssignment(data.assign)
        result = self._get_result(kw, data, assignment, context.variables)
        with StatusReporter(data, result, context, implementation=kw):
            assignment.validate_assignment()
            self._dry_run(kw, data.args, result, context)

    def _dry_run(self, kw, args, result, context):
        if self.pre_run_messages:
            for message in self.pre_run_messages:
                context.output.message(message)
        self._resolve_arguments(kw, args)
        with context.user_keyword(kw):
            if kw.timeout:
                timeout = KeywordTimeout(kw.timeout, context.variables)
                result.timeout = str(timeout)
            error, _ = self._execute(kw, context)
            if error:
                raise error


class EmbeddedArgumentsRunner(UserKeywordRunner):

    def __init__(self, keyword, name):
        super().__init__(keyword, name)
        self.embedded_args = keyword.embedded.match(name).groups()

    def _resolve_arguments(self, kw, args, variables=None):
        result = super()._resolve_arguments(kw, args, variables)
        if variables:
            embedded = [variables.replace_scalar(e) for e in self.embedded_args]
            self.embedded_args = kw.embedded.map(embedded)
        return result

    def _set_arguments(self, kw, args, context):
        variables = context.variables
        for name, value in self.embedded_args:
            variables[f'${{{name}}}'] = value
        super()._set_arguments(kw, args, context)

    def _trace_log_args_message(self, kw, variables):
        args = [f'${{{arg}}}' for arg in kw.embedded.args]
        args += self._format_args_for_trace_logging(kw.args)
        return self._format_trace_log_args_message(args, variables)

    def _get_result(self, kw, data, assignment, variables):
        result = super()._get_result(kw, data, assignment, variables)
        result.source_name = kw.name
        return result
