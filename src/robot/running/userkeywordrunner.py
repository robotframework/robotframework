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

from typing import TYPE_CHECKING

from robot.errors import (
    DataError, ExecutionFailed, ExecutionPassed, ExecutionStatus, PassExecution,
    ReturnFromKeyword, UserKeywordExecutionFailed, VariableError
)
from robot.result import Keyword as KeywordResult
from robot.utils import DotDict, getshortdoc, prepr, split_tags_from_doc
from robot.variables import is_list_variable, VariableAssignment

from .arguments import ArgumentSpec, DefaultValue
from .bodyrunner import BodyRunner, KeywordRunner
from .model import Keyword as KeywordData
from .statusreporter import StatusReporter
from .timeouts import KeywordTimeout

if TYPE_CHECKING:
    from .resourcemodel import UserKeyword


class UserKeywordRunner:

    def __init__(self, keyword: "UserKeyword", name: "str|None" = None):
        self.keyword = keyword
        self.name = name or keyword.name
        self.pre_run_messages = ()

    def run(self, data: KeywordData, result: KeywordResult, context, run=True):
        kw = self.keyword.bind(data)
        assignment = VariableAssignment(data.assign)
        self._config_result(result, data, kw, assignment, context.variables)
        with StatusReporter(data, result, context, run, implementation=kw):
            self._validate(kw)
            if kw.private:
                context.warn_on_invalid_private_call(kw)
            with assignment.assigner(context) as assigner:
                if run:
                    return_value = self._run(data, kw, result, context)
                    assigner.assign(return_value)
                    return return_value

    def _config_result(
        self,
        result: KeywordResult,
        data: KeywordData,
        kw: "UserKeyword",
        assignment,
        variables,
    ):
        args = tuple(data.args)
        if data.named_args:
            args += tuple(f"{n}={v}" for n, v in data.named_args.items())
        doc = variables.replace_string(kw.doc, ignore_errors=True)
        doc, tags = split_tags_from_doc(doc)
        tags = variables.replace_list(kw.tags, ignore_errors=True) + tags
        result.config(
            name=self.name,
            owner=kw.owner.name,
            doc=getshortdoc(doc),
            args=args,
            assign=tuple(assignment),
            tags=tags,
            type=data.type,
        )

    def _validate(self, kw: "UserKeyword"):
        if kw.error:
            raise DataError(kw.error)
        if not kw.name:
            raise DataError("User keyword name cannot be empty.")
        if not kw.body:
            raise DataError("User keyword cannot be empty.")

    def _run(
        self,
        data: KeywordData,
        kw: "UserKeyword",
        result: KeywordResult,
        context,
    ):
        if self.pre_run_messages:
            for message in self.pre_run_messages:
                context.output.message(message)
        variables = context.variables
        positional, named = self._resolve_arguments(data, kw, variables)
        with context.user_keyword(kw):
            self._set_arguments(kw, positional, named, context)
            if kw.timeout:
                timeout = KeywordTimeout(kw.timeout, variables)
                result.timeout = str(timeout) if timeout else None
            else:
                timeout = None
            with context.keyword_timeout(timeout):
                exception, return_value = self._execute(kw, result, context)
                if exception and not exception.can_continue(context):
                    if context.in_teardown and exception.keyword_timeout:
                        # Allow execution to continue on teardowns after timeout.
                        # https://github.com/robotframework/robotframework/issues/3398
                        exception.keyword_timeout = False
                    raise exception
                return_value = self._handle_return_value(return_value, variables)
                if exception:
                    exception.return_value = return_value
                    raise exception
                return return_value

    def _resolve_arguments(self, data: KeywordData, kw: "UserKeyword", variables=None):
        return kw.resolve_arguments(data.args, data.named_args, variables)

    def _set_arguments(self, kw: "UserKeyword", positional, named, context):
        variables = context.variables
        positional, named = kw.args.map(positional, named, replace_defaults=False)
        self._set_variables(kw.args, positional, named, variables)
        context.output.trace(
            lambda: self._trace_log_args_message(kw, variables), write_if_flat=False
        )

    def _set_variables(self, spec: ArgumentSpec, positional, named, variables):
        positional, var_positional = self._separate_positional(spec, positional)
        named_only, var_named = self._separate_named(spec, named)
        for name, value in (*zip(spec.positional, positional), *named_only):
            if isinstance(value, DefaultValue):
                value = value.resolve(variables)
                info = spec.types.get(name)
                if info:
                    value = info.convert(value, name, kind="Default value for argument")
            variables[f"${{{name}}}"] = value
        if spec.var_positional:
            variables[f"@{{{spec.var_positional}}}"] = var_positional
        if spec.var_named:
            variables[f"&{{{spec.var_named}}}"] = DotDict(var_named)

    def _separate_positional(self, spec: ArgumentSpec, positional):
        if not spec.var_positional:
            return positional, []
        count = len(spec.positional)
        return positional[:count], positional[count:]

    def _separate_named(self, spec: ArgumentSpec, named):
        named_only = []
        var_named = []
        for name, value in named:
            target = named_only if name in spec.named_only else var_named
            target.append((name, value))
        return named_only, var_named

    def _trace_log_args_message(self, kw: "UserKeyword", variables):
        return self._format_trace_log_args_message(
            self._format_args_for_trace_logging(kw.args), variables
        )

    def _format_args_for_trace_logging(self, spec: ArgumentSpec):
        args = [f"${{{arg}}}" for arg in spec.positional]
        if spec.var_positional:
            args.append(f"@{{{spec.var_positional}}}")
        if spec.named_only:
            args.extend(f"${{{arg}}}" for arg in spec.named_only)
        if spec.var_named:
            args.append(f"&{{{spec.var_named}}}")
        return args

    def _format_trace_log_args_message(self, args, variables):
        args = " | ".join(f"{name}={prepr(variables[name])}" for name in args)
        return f"Arguments: [ {args} ]"

    def _execute(self, kw: "UserKeyword", result: KeywordResult, context):
        if context.dry_run and kw.tags.robot("no-dry-run"):
            return None, None
        error = success = return_value = None
        if kw.setup:
            error = self._run_setup_or_teardown(kw.setup, result.setup, context)
        try:
            BodyRunner(context, run=not error).run(kw, result)
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
                td_error = self._run_setup_or_teardown(
                    kw.teardown, result.teardown, context
                )
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
            raise VariableError(
                f"Replacing variables from keyword return value failed: {err}"
            )
        if len(return_value) != 1 or contains_list_var:
            return return_value
        return return_value[0]

    def _run_setup_or_teardown(self, data: KeywordData, result: KeywordResult, context):
        try:
            KeywordRunner(context).run(data, result, setup_or_teardown=True)
        except PassExecution:
            return None
        except ExecutionStatus as err:
            return err
        return None

    def dry_run(self, data: KeywordData, result: KeywordResult, context):
        kw = self.keyword.bind(data)
        assignment = VariableAssignment(data.assign)
        self._config_result(result, data, kw, assignment, context.variables)
        with StatusReporter(data, result, context, implementation=kw):
            self._validate(kw)
            assignment.validate_assignment()
            self._dry_run(data, kw, result, context)

    def _dry_run(
        self,
        data: KeywordData,
        kw: "UserKeyword",
        result: KeywordResult,
        context,
    ):
        if self.pre_run_messages:
            for message in self.pre_run_messages:
                context.output.message(message)
        self._resolve_arguments(data, kw)
        with context.user_keyword(kw):
            if kw.timeout:
                timeout = KeywordTimeout(kw.timeout, context.variables)
                result.timeout = str(timeout)
            error, _ = self._execute(kw, result, context)
            if error:
                raise error


class EmbeddedArgumentsRunner(UserKeywordRunner):

    def __init__(self, keyword: "UserKeyword", name: str):
        super().__init__(keyword, name)
        self.embedded_args = keyword.embedded.parse_args(name)

    def _resolve_arguments(self, data: KeywordData, kw: "UserKeyword", variables=None):
        result = super()._resolve_arguments(data, kw, variables)
        if variables:
            embedded = [variables.replace_scalar(e) for e in self.embedded_args]
            self.embedded_args = kw.embedded.map(embedded)
        return result

    def _set_arguments(self, kw: "UserKeyword", positional, named, context):
        variables = context.variables
        for name, value in self.embedded_args:
            variables[f"${{{name}}}"] = value
        super()._set_arguments(kw, positional, named, context)

    def _trace_log_args_message(self, kw: "UserKeyword", variables):
        args = [f"${{{arg}}}" for arg in kw.embedded.args]
        args += self._format_args_for_trace_logging(kw.args)
        return self._format_trace_log_args_message(args, variables)

    def _config_result(
        self,
        result: KeywordResult,
        data: KeywordData,
        kw: "UserKeyword",
        assignment,
        variables,
    ):
        super()._config_result(result, data, kw, assignment, variables)
        result.source_name = kw.name
