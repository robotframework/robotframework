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

from robot.utils import (format_assign_message, get_elapsed_time,
                         get_error_message, get_timestamp, plural_or_not, frange)
from robot.errors import (ContinueForLoop, DataError, ExecutionFailed,
                          ExecutionFailures, ExecutionPassed, ExitForLoop,
                          HandlerExecutionFailed)

from robot.variables import is_scalar_var, VariableAssigner


class Keywords(object):

    def __init__(self, steps, templated=False):
        self._keywords = []
        self._templated = templated
        for s in steps:
            self._add_step(s)

    def _add_step(self, step):
        if step.is_comment():
            return
        if step.is_for_loop():
            keyword = ForLoop(step, self._templated)
        else:
            keyword = Keyword(step.keyword, step.args, step.assign)
        self.add_keyword(keyword)

    def add_keyword(self, keyword):
        self._keywords.append(keyword)

    def run(self, context):
        errors = []
        for kw in self._keywords:
            try:
                kw.run(context)
            except ExecutionPassed, exception:
                exception.set_earlier_failures(errors)
                raise exception
            except ExecutionFailed, exception:
                errors.extend(exception.get_errors())
                if not exception.can_continue(context.in_teardown,
                                              self._templated,
                                              context.dry_run):
                    break
        if errors:
            raise ExecutionFailures(errors)

    def __nonzero__(self):
        return bool(self._keywords)

    def __iter__(self):
        return iter(self._keywords)


class _BaseKeyword:

    def __init__(self, name='', args=None, doc='', timeout='', type='kw'):
        self.name = name
        self.args = args or []
        self.doc = doc
        self.timeout = timeout
        self.type = type
        self.message = ''
        self.status = 'NOT_RUN'

    @property
    def passed(self):
        return self.status == 'PASS'

    def serialize(self, serializer):
        serializer.start_keyword(self)
        serializer.end_keyword(self)

    def _get_status(self, error):
        if not error:
            return 'PASS'
        if isinstance(error, ExecutionPassed) and not error.earlier_failures:
            return 'PASS'
        return 'FAIL'


class Keyword(_BaseKeyword):

    def __init__(self, name, args, assign=None, type='kw'):
        _BaseKeyword.__init__(self, name, args, type=type)
        self.assign = assign or []
        self.handler_name = name

    def run(self, context):
        handler = self._start(context)
        try:
            return_value = self._run(handler, context)
        except ExecutionFailed, err:
            self.status = self._get_status(err)
            self._end(context, error=err)
            raise
        else:
            if not (context.dry_run and handler.type == 'library'):
                self.status = 'PASS'
            self._end(context, return_value)
            return return_value

    def _start(self, context):
        handler = context.get_handler(self.handler_name)
        handler.init_keyword(context.variables)
        self.name = self._get_name(handler.longname)
        self.doc = handler.shortdoc
        self.timeout = getattr(handler, 'timeout', '')
        self.starttime = get_timestamp()
        context.start_keyword(self)
        if self.doc.startswith('*DEPRECATED*'):
            msg = self.doc.replace('*DEPRECATED*', '', 1).strip()
            name = self.name.split('} = ', 1)[-1]  # Remove possible variable
            context.warn("Keyword '%s' is deprecated. %s" % (name, msg))
        return handler

    def _get_name(self, handler_longname):
        if not self.assign:
            return handler_longname
        return '%s = %s' % (', '.join(a.rstrip('= ') for a in self.assign),
                            handler_longname)

    def _run(self, handler, context):
        try:
            return handler.run(context, self.args[:])
        except ExecutionFailed:
            raise
        except:
            self._report_failure(context)

    def _end(self, context, return_value=None, error=None):
        self.endtime = get_timestamp()
        self.elapsedtime = get_elapsed_time(self.starttime, self.endtime)
        if error and self.type == 'teardown':
            self.message = unicode(error)
        try:
            if not error or error.can_continue(context.in_teardown):
                self._set_variables(context, return_value, error)
        finally:
            context.end_keyword(self)

    def _set_variables(self, context, return_value, error):
        if error:
            return_value = error.return_value
        try:
            VariableAssigner(self.assign).assign(context, return_value)
        except DataError, err:
            self.status = 'FAIL'
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


class ForLoop(_BaseKeyword):

    def __init__(self, forstep, templated=False):
        _BaseKeyword.__init__(self, self._get_name(forstep), type='for')
        self.vars = forstep.vars
        self.items = forstep.items
        self.range = forstep.range
        self.keywords = Keywords(forstep.steps, templated)
        self._templated = templated

    def _get_name(self, data):
        return '%s %s [ %s ]' % (' | '.join(data.vars),
                                 'IN' if not data.range else 'IN RANGE',
                                 ' | '.join(data.items))

    def run(self, context):
        self.starttime = get_timestamp()
        context.start_keyword(self)
        error = self._run_with_error_handling(self._validate_and_run, context)
        self.status = self._get_status(error)
        self.endtime = get_timestamp()
        self.elapsedtime = get_elapsed_time(self.starttime, self.endtime)
        context.end_keyword(self)
        if error:
            raise error

    def _run_with_error_handling(self, runnable, context):
        try:
            runnable(context)
        except ExecutionFailed, err:
            return err
        except DataError, err:
            msg = unicode(err)
            context.output.fail(msg)
            return ExecutionFailed(msg, syntax=True)
        else:
            return None

    def _validate_and_run(self, context):
        self._validate()
        self._run(context)

    def _validate(self):
        if not self.vars:
            raise DataError('FOR loop has no loop variables.')
        for var in self.vars:
            if not is_scalar_var(var):
                raise DataError("Invalid FOR loop variable '%s'." % var)
        if not self.items:
            raise DataError('FOR loop has no loop values.')
        if not self.keywords:
            raise DataError('FOR loop contains no keywords.')

    def _run(self, context):
        errors = []
        items, iteration_steps = self._get_items_and_iteration_steps(context)
        for i in iteration_steps:
            values = items[i:i+len(self.vars)]
            exception = self._run_one_round(context, self.vars, values)
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

    def _get_items_and_iteration_steps(self, context):
        if context.dry_run:
            return self.vars, [0]
        items = self._replace_vars_from_items(context.variables)
        return items, range(0, len(items), len(self.vars))

    def _run_one_round(self, context, variables, values):
        foritem = _ForItem(variables, values)
        context.start_keyword(foritem)
        for var, value in zip(variables, values):
            context.variables[var] = value
        error = self._run_with_error_handling(self.keywords.run, context)
        foritem.end(self._get_status(error))
        context.end_keyword(foritem)
        return error

    def _replace_vars_from_items(self, variables):
        items = variables.replace_list(self.items)
        if self.range:
            items = self._get_range_items(items)
        if len(items) % len(self.vars) == 0:
            return items
        raise DataError('Number of FOR loop values should be multiple of '
                        'variables. Got %d variables but %d value%s.'
                        % (len(self.vars), len(items), plural_or_not(items)))

    def _get_range_items(self, items):
        try:
            items = [self._to_number_with_arithmetics(item) for item in items]
        except:
            raise DataError('Converting argument of FOR IN RANGE failed: %s'
                            % get_error_message())
        if not 1 <= len(items) <= 3:
            raise DataError('FOR IN RANGE expected 1-3 arguments, '
                            'got %d instead.' % len(items))
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
            raise TypeError("Expected number, got '%s' instead." % item)
        return number


class _ForItem(_BaseKeyword):

    def __init__(self, vars, items):
        name = ', '.join(format_assign_message(var, item)
                         for var, item in zip(vars, items))
        _BaseKeyword.__init__(self, name, type='foritem')
        self.starttime = get_timestamp()

    def end(self, status):
        self.status = status
        self.endtime = get_timestamp()
        self.elapsedtime = get_elapsed_time(self.starttime, self.endtime)
