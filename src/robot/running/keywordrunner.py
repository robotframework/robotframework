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

from robot.model import SuiteVisitor
from robot.errors import ExecutionFailed, DataError, HandlerExecutionFailed, ExecutionPassed, ExitForLoop, ContinueForLoop, ExecutionFailures
from robot.utils import get_timestamp, get_error_message, frange, type_name, plural_or_not, format_assign_message
from robot.result.keyword import Keyword as KeywordResult
from robot.variables import is_scalar_var, VariableAssigner


class KeywordRunner(object):

    def __init__(self, context, templated=False):
        self._context = context
        self._templated = templated


    def run_keywords(self, keywords):
        errors = []
        for kw in keywords:
            try:
                self.run_keyword(kw)
            except ExecutionPassed as exception:
                exception.set_earlier_failures(errors)
                raise exception
            except ExecutionFailed as exception:
                errors.extend(exception.get_errors())
                if not exception.can_continue(self._context.in_teardown,
                                              self._templated,
                                              self._context.dry_run):
                    break
        if errors:
            raise ExecutionFailures(errors)

    def run_keyword(self, kw, name=None):
        if kw.type == kw.FOR_LOOP_TYPE:
            runner = ForLoopRunner(self._context, self._templated)
        else:
            runner = NormalRunner(self._context)
        runner.run(kw, name=name)



class NormalRunner(object):

    def __init__(self, context):
        self._context = context

    def run(self, kw, name=None):
        context = self._context
        handler = context.get_handler(name or kw.name)
        handler.init_keyword(context.variables)
        result = KeywordResult(name=self._get_name(kw.assign, handler.longname),
                               doc=handler.shortdoc,
                               args=kw.args,
                               assign=kw.assign,
                               timeout=getattr(handler, 'timeout', ''),
                               type=kw.type,
                               status='NOT_RUN',
                               starttime=get_timestamp())
        context.start_keyword(result)
        self._warn_if_deprecated(handler.longname, handler.shortdoc, context)
        try:
            return_value = self._run(handler, kw, context)
        except ExecutionFailed as err:
            result.status = self._get_status(err)
            self._end(result, context, error=err)
            raise
        else:
            if not (context.dry_run and handler.type == 'library'):
                result.status = 'PASS'
            self._end(result, context, return_value)

    def _warn_if_deprecated(self, name, doc, context):
        if doc.startswith('*DEPRECATED') and '*' in doc[1:]:
            message = ' ' + doc.split('*', 2)[-1].strip()
            context.warn("Keyword '%s' is deprecated.%s" % (name, message))

    def _get_name(self, assign, handler_longname):
        if not assign:
            return handler_longname
        return '%s = %s' % (', '.join(a.rstrip('= ') for a in assign),
                            handler_longname)

    def _run(self, handler, kw, context):
        try:
            # TODO clean this away from self
            self._variable_assigner = VariableAssigner(kw.assign)
            return handler.run(context, kw.args[:])
        except ExecutionFailed:
            raise
        except:
            self._report_failure(context)

    def _get_status(self, error):
        if not error:
            return 'PASS'
        if isinstance(error, ExecutionPassed) and not error.earlier_failures:
            return 'PASS'
        return 'FAIL'

    def _end(self, result, context, return_value=None, error=None):
        result.endtime = get_timestamp()
        if error and result.type == 'teardown':
            result.message = unicode(error)
        try:
            if not error or error.can_continue(context.in_teardown):
                self._set_variables(result, context, return_value, error)
        finally:
            context.end_keyword(result)

    def _set_variables(self, result, context, return_value, error):
        if error:
            return_value = error.return_value
        try:
            self._variable_assigner.assign(context, return_value)
        except DataError as err:
            result.status = 'FAIL'
            msg = unicode(err)
            context.output.fail(msg)
            raise ExecutionFailed(msg, syntax=True)

    def _report_failure(self, context):
        failure = HandlerExecutionFailed()
        if failure.timeout:
            context.timeout_occurred = True
        context.output.fail(failure.full_message)
        if failure.traceback:
            context.output.debug(failure.traceback)
        raise failure


class ForLoopRunner(object):

    def __init__(self, context, templated=False):
        self._context = context
        self._templated = templated

    def run(self, kw, name=None):
        context = self._context
        result = KeywordResult(name=self._get_name(kw),
                               args=kw.args,
                               assign=kw.assign,
                               type=kw.FOR_LOOP_TYPE,
                               starttime=get_timestamp())
        context.start_keyword(result)
        error = self._run_with_error_handling(self._validate_and_run, context, kw)
        result.status = self._get_status(error)
        result.endtime = get_timestamp()
        context.end_keyword(result)
        if error:
            raise error

    def _get_name(self, data):
        return '%s %s [ %s ]' % (' | '.join(data.vars),
                                 'IN' if not data.range else 'IN RANGE',
                                 ' | '.join(data.items))

    def _run_with_error_handling(self, runnable, *args):
        try:
            runnable(*args)
        except ExecutionFailed as err:
            return err
        except DataError as err:
            msg = unicode(err)
            self._context.output.fail(msg)
            return ExecutionFailed(msg, syntax=True)
        else:
            return None

    def _validate_and_run(self, context, data):
        self._validate(data)
        self._run(context, data)

    def _validate(self, data):
        if not data.vars:
            raise DataError('FOR loop has no loop variables.')
        for var in data.vars:
            if not is_scalar_var(var):
                raise DataError("Invalid FOR loop variable '%s'." % var)
        if not data.items:
            raise DataError('FOR loop has no loop values.')
        if not data.keywords:
            raise DataError('FOR loop contains no keywords.')

    def _run(self, context, data):
        errors = []
        items, iteration_steps = self._get_items_and_iteration_steps(context, data)
        for i in iteration_steps:
            values = items[i:i+len(data.vars)]
            exception = self._run_one_round(context, data, values)
            if exception:
                if isinstance(exception, ExitForLoop):
                    if exception.earlier_failures:
                        errors.extend(exception.earlier_failures.get_errors())
                    break
                if isinstance(exception, ContinueForLoop):
                    if exception.earlier_failures:
                        errors.extend(exception.earlier_failures.get_errors())
                    continue
                if isinstance(exception, ExecutionPassed):
                    exception.set_earlier_failures(errors)
                    raise exception
                errors.extend(exception.get_errors())
                if not exception.can_continue(context.in_teardown,
                                              self._templated,
                                              context.dry_run):
                    break
        if errors:
            raise ExecutionFailures(errors)

    def _get_items_and_iteration_steps(self, context, data):
        if context.dry_run:
            return data.vars, [0]
        items = self._replace_vars_from_items(context.variables, data)
        return items, range(0, len(items), len(data.vars))

    def _replace_vars_from_items(self, variables, data):
        items = variables.replace_list(data.items)
        if data.range:
            items = self._get_range_items(items)
        if len(items) % len(data.vars) == 0:
            return items
        raise DataError('Number of FOR loop values should be multiple of '
                        'variables. Got %d variables but %d value%s.'
                        % (len(data.vars), len(items), plural_or_not(items)))

    def _get_range_items(self, items):
        try:
            items = [self._to_number_with_arithmetics(item) for item in items]
        except:
            raise DataError('Converting argument of FOR IN RANGE failed: %s'
                            % get_error_message())
        if not 1 <= len(items) <= 3:
            raise DataError('FOR IN RANGE expected 1-3 arguments, got %d.'
                            % len(items))
        return frange(*items)

    def _to_number_with_arithmetics(self, item):
        if isinstance(item, (int, long, float)):
            return item
        item = str(item)
        # eval() would also convert to int or float, but it sometimes very
        # mysteriously fails with IronPython (seems to be related to timeouts)
        # and thus it's better to avoid it.
        for converter in int, float:
            try:
                return converter(item)
            except ValueError:
                pass
        number = eval(item, {})
        if not isinstance(number, (int, long, float)):
            raise TypeError("Expected number, got %s." % type_name(item))
        return number

    def _run_one_round(self, context, data, values):
        result = KeywordResult(name=', '.join(format_assign_message(var, item)
                                              for var, item in zip(data.vars, values)),
                               type=data.FOR_ITEM_TYPE,
                               starttime=get_timestamp())
        context.start_keyword(result)
        for var, value in zip(data.vars, values):
            context.variables[var] = value
        runner = KeywordRunner(self._context, self._templated)
        error = self._run_with_error_handling(runner.run_keywords, data.keywords)
        result.status = self._get_status(error)
        result.endtime = get_timestamp()
        context.end_keyword(result)
        return error

    def _get_status(self, error):
        if not error:
            return 'PASS'
        if isinstance(error, ExecutionPassed) and not error.earlier_failures:
            return 'PASS'
        return 'FAIL'
