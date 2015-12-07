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

from robot.errors import (ExecutionFailed, ReturnFromKeyword, ExecutionPassed,
                          UserKeywordExecutionFailed, DataError,
                          HandlerExecutionFailed, VariableError, PassExecution)
from robot.result.keyword import Keyword as KeywordResult
from robot.utils import (ErrorDetails, DotDict, prepr)
from robot.variables import is_list_var, is_scalar_var, VariableAssigner

from .arguments import ArgumentMapper, ArgumentResolver
from .keywordrunner import KeywordRunner, StatusReporter, SyntaxErrorReporter


class UserKeywordRunner(object):

    def __init__(self, handler):
        self._handler = handler

    @property
    def arguments(self):
        return self._handler.arguments

    def run(self, kw, context):
        assigner = VariableAssigner(kw.assign)
        handler = self._handler
        result = KeywordResult(kwname=handler.name or '',
                               libname=handler.libname or '',
                               doc=handler.shortdoc,
                               args=kw.args,
                               assign=assigner.assignment,
                               timeout=handler.timeout,
                               tags=handler.tags,
                               type=kw.type)
        with StatusReporter(context, result):
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
            return_value = self._handler_run(context, args)
        except ExecutionFailed as err:
            exception = err
        except:
            exception = self._get_and_report_failure(context)
        if exception:
            return_value = exception.return_value
        return return_value, exception

    def _handler_run(self, context, args):
        positional, named = ArgumentResolver(self.arguments).resolve(args, context.variables)
        with context.user_keyword(self._handler):
            args, kwargs = ArgumentMapper(self.arguments).map(positional, named, context.variables)
            return self._normal_run(context, args, kwargs)

    def _normal_run(self, context, args, kwargs):
        error, return_ = self._execute(context, args, kwargs)
        if error and not error.can_continue(context.in_teardown):
            raise error
        return_value = self._get_return_value(context.variables, return_)
        if error:
            error.return_value = return_value
            raise error
        return return_value

    def _get_return_value(self, variables, return_):
        ret = self._handler.return_value if not return_ else return_.return_value
        if not ret:
            return None
        contains_list_var = any(is_list_var(item) for item in ret)
        try:
            ret = variables.replace_list(ret)
        except DataError as err:
            raise VariableError('Replacing variables from keyword return value '
                                'failed: %s' % err.message)
        if len(ret) != 1 or contains_list_var:
            return ret
        return ret[0]

    def _execute(self, context, positional, kwargs):
        self._set_variables(positional, kwargs, context.variables)
        context.output.trace(lambda: self._log_args(context.variables))
        self._verify_keyword_is_valid()
        error = return_ = pass_ = None
        runner = KeywordRunner(context)
        try:
            runner.run_keywords(self._handler.keywords)
        except ReturnFromKeyword as exception:
            return_ = exception
            error = exception.earlier_failures
        except ExecutionPassed as exception:
            pass_ = exception
            error = exception.earlier_failures
        except ExecutionFailed as exception:
            error = exception
        with context.keyword_teardown(error):
            td_error = self._run_teardown(context)
        if error or td_error:
            error = UserKeywordExecutionFailed(error, td_error)
        return error or pass_, return_

    def _set_variables(self, positional, kwargs, variables):
        before_varargs, varargs = self._split_args_and_varargs(positional)
        for name, value in zip(self.arguments.positional, before_varargs):
            variables['${%s}' % name] = value
        if self.arguments.varargs:
            variables['@{%s}' % self.arguments.varargs] = varargs
        if self.arguments.kwargs:
            variables['&{%s}' % self.arguments.kwargs] = DotDict(kwargs)

    def _split_args_and_varargs(self, args):
        if not self.arguments.varargs:
            return args, []
        positional = len(self.arguments.positional)
        return args[:positional], args[positional:]

    def _get_and_report_failure(self, context):
        failure = HandlerExecutionFailed(ErrorDetails())
        if failure.timeout:
            context.timeout_occurred = True
        context.fail(failure.full_message)
        if failure.traceback:
            context.debug(failure.traceback)
        return failure

    def _log_args(self, variables):
        args = ['${%s}' % arg for arg in self.arguments.positional]
        if self.arguments.varargs:
            args.append('@{%s}' % self.arguments.varargs)
        if self.arguments.kwargs:
            args.append('&{%s}' % self.arguments.kwargs)
        args = ['%s=%s' % (name, prepr(variables[name])) for name in args]
        return 'Arguments: [ %s ]' % ' | '.join(args)

    def _run_teardown(self, context):
        if not self._handler.teardown:
            return None
        try:
            name = context.variables.replace_string(self._handler.teardown.name)
        except DataError as err:
            return ExecutionFailed(err.message, syntax=True)
        if name.upper() in ('', 'NONE'):
            return None
        runner = KeywordRunner(context)
        try:
            runner.run_keyword(self._handler.teardown, name)
        except PassExecution:
            return None
        except ExecutionFailed as err:
            return err
        return None

    def _verify_keyword_is_valid(self):
        if not (self._handler.keywords or self._handler.return_value):
            raise DataError("User keyword '%s' contains no keywords."
                            % self._handler.name)


class EmbeddedArgsUserKeywordRunner(UserKeywordRunner):


    def _handler_run(self, context, args):
        # Validates that no arguments given.
        ArgumentResolver(self.arguments).resolve(args, context.variables)
        arguments = [(n, context.variables.replace_scalar(v)) for n, v in self._handler.embedded_args]
        with context.user_keyword(self._handler):
            for name, value in arguments:
                context.variables['${%s}' % name] = value
            return self._normal_run(context, [], {})


class UserKeywordDryRunner(object):

    def __init__(self, handler):
        self._handler = handler

    @property
    def arguments(self):
        return self._handler.arguments

    def run(self, kw, context):
        assigner = VariableAssigner(kw.assign)
        handler = self._handler
        result = KeywordResult(kwname=handler.name or '',
                               libname=handler.libname or '',
                               doc=handler.shortdoc,
                               args=kw.args,
                               assign=assigner.assignment,
                               timeout=handler.timeout,
                               tags=handler.tags,
                               type=kw.type)
        with StatusReporter(context, result):
            self._warn_if_deprecated(result.name, result.doc, context)
            self._run_and_assign(context, kw.args, assigner)

    def _warn_if_deprecated(self, name, doc, context):
        if doc.startswith('*DEPRECATED') and '*' in doc[1:]:
            message = ' ' + doc.split('*', 2)[-1].strip()
            context.warn("Keyword '%s' is deprecated.%s" % (name, message))

    def _run_and_assign(self, context, args, assigner):
        syntax_error_reporter = SyntaxErrorReporter(context)
        with syntax_error_reporter:
            assigner.validate_assignment()
        self._run(context, args)

    def _run(self, context, args):
        try:
            self._handler_dry_run(context, args)
        except ExecutionFailed as err:
            raise err
        except:
            raise self._get_and_report_failure(context)

    def _handler_dry_run(self, context, args):
        arguments = ArgumentResolver(self.arguments).resolve(args)
        with context.user_keyword(self._handler):
            args, kwargs = ArgumentMapper(self.arguments).map(*arguments)
            self._execute(context, args, kwargs)

    def _execute(self, context, positional, kwargs):
        self._set_variables(positional, kwargs, context.variables)
        context.output.trace(lambda: self._log_args(context.variables))
        self._verify_keyword_is_valid()
        error = None
        runner = KeywordRunner(context)
        try:
            runner.run_keywords(self._handler.keywords)
        except ExecutionFailed as exception:
            error = exception
        with context.keyword_teardown(error):
            td_error = self._run_teardown(context)
        if error or td_error:
            raise UserKeywordExecutionFailed(error, td_error)

    def _set_variables(self, positional, kwargs, variables):
        before_varargs, varargs = self._split_args_and_varargs(positional)
        for name, value in zip(self.arguments.positional, before_varargs):
            variables['${%s}' % name] = value
        if self.arguments.varargs:
            variables['@{%s}' % self.arguments.varargs] = varargs
        if self.arguments.kwargs:
            variables['&{%s}' % self.arguments.kwargs] = DotDict(kwargs)

    def _split_args_and_varargs(self, args):
        if not self.arguments.varargs:
            return args, []
        positional = len(self.arguments.positional)
        return args[:positional], args[positional:]

    def _get_and_report_failure(self, context):
        failure = HandlerExecutionFailed(ErrorDetails())
        if failure.timeout:
            context.timeout_occurred = True
        context.fail(failure.full_message)
        if failure.traceback:
            context.debug(failure.traceback)
        return failure

    def _log_args(self, variables):
        args = ['${%s}' % arg for arg in self.arguments.positional]
        if self.arguments.varargs:
            args.append('@{%s}' % self.arguments.varargs)
        if self.arguments.kwargs:
            args.append('&{%s}' % self.arguments.kwargs)
        args = ['%s=%s' % (name, prepr(variables[name])) for name in args]
        return 'Arguments: [ %s ]' % ' | '.join(args)

    def _run_teardown(self, context):
        if not self._handler.teardown:
            return None
        try:
            name = context.variables.replace_string(self._handler.teardown.name)
        except DataError as err:
            return ExecutionFailed(err.message, syntax=True)
        if name.upper() in ('', 'NONE'):
            return None
        runner = KeywordRunner(context)
        try:
            runner.run_keyword(self._handler.teardown, name)
        except PassExecution:
            return None
        except ExecutionFailed as err:
            return err
        return None

    def _verify_keyword_is_valid(self):
        if not (self._handler.keywords or self._handler.return_value):
            raise DataError("User keyword '%s' contains no keywords."
                            % self._handler.name)


class EmbeddedArgsUserKeywordDryRunner(UserKeywordDryRunner):

    def _handler_dry_run(self, context, args):
        # Validates that no arguments given.
        ArgumentResolver(self.arguments).resolve(args)
        with context.user_keyword(self._handler):
            self._execute(context, [], {})
