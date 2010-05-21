#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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

from robot import utils
from robot.errors import (DataError, ExecutionFailed, ExecutionFailures,
                          HandlerExecutionFailed)
from robot.common import BaseKeyword
from robot.variables import is_var, is_list_var, is_scalar_var


class Keywords(object):

    def __init__(self, steps):
        self._keywords = [_KeywordFactory(step) for step in steps]

    def run(self, context):
        errors = []
        for kw in self._keywords:
            try:
                kw.run(context)
            except ExecutionFailed, err:
                errors.extend(err.get_errors())
                if not err.cont:
                    break
        if errors:
            raise ExecutionFailures(errors)

    def __nonzero__(self):
        return bool(self._keywords)

    def __iter__(self):
        return iter(self._keywords)


def _KeywordFactory(step):
    if not hasattr(step, 'steps'):
        return Keyword(step.keyword, step.args, step.assign)
    return ForLoop(step)


class Keyword(BaseKeyword):

    def __init__(self, name, args, assign=None, type='kw'):
        BaseKeyword.__init__(self, name, args, type=type)
        self.assign = _Assignment(name, assign or [])
        self.handler_name = name

    def run(self, context):
        handler = self._start(context)
        try:
            return_value = self._run(handler, context)
        except ExecutionFailed, err:
            self.status = 'FAIL'
            self._end(context, error=err)
            raise
        else:
            if not (context.dry_run and handler.type == 'library'):
                self.status = 'PASS'
            self._end(context, return_value)
            return return_value

    def _start(self, context):
        handler = context.get_handler(self.handler_name)
        handler.init_keyword(context.get_current_vars())
        self.name = self._get_name(handler.longname)
        self.doc = handler.shortdoc
        self.starttime = utils.get_timestamp()
        context.start_keyword(self)
        if self.doc.startswith('*DEPRECATED*'):
            msg = self.doc.replace('*DEPRECATED*', '', 1).strip()
            name = self.name.split('} = ', 1)[-1]  # Remove possible variable
            context.warn("Keyword '%s' is deprecated. %s" % (name, msg))
        return handler

    def _get_name(self, handler_name):
        if not self.assign:
            return handler_name
        return '%s = %s' % (', '.join(self.assign), handler_name)

    def _end(self, context, return_value=None, error=None):
        self.endtime = utils.get_timestamp()
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)
        try:
            if not error or error.cont:
                self._set_variables(context, return_value)
                context.trace('Return: %s' % utils.safe_repr(return_value))
        finally:
            context.end_keyword(self)

    def _run(self, handler, context):
        try:
            return handler.run(context, self.args[:])
        except ExecutionFailed:
            raise
        except:
            self._report_failure(context)

    def _set_variables(self, context, return_value):
        try:
            self.assign.set_variables(context, return_value)
        except DataError, err:
            msg = unicode(err)
            context.output.fail(msg)
            raise ExecutionFailed(msg, syntax=True)

    def _report_failure(self, context):
        error_details = utils.ErrorDetails()
        context.output.fail(error_details.message)
        if error_details.traceback:
            context.output.debug(error_details.traceback)
        is_teardown = self._in_test_or_suite_teardown(context.namespace)
        raise HandlerExecutionFailed(error_details, is_teardown, context.dry_run)

    def _in_test_or_suite_teardown(self, namespace):
        test_or_suite = namespace.test or namespace.suite
        return test_or_suite.status != 'RUNNING'


class _Assignment(object):

    def __init__(self, keyword, assign):
        self.keyword = keyword
        # TODO: Cleanup handling errors
        try:
            self.scalar_vars, self.list_var = self._split_assing(assign)
            self._error = None
        except DataError, err:
            self.scalar_vars, self.list_var = [], None
            self._error = err

    def _split_assing(self, assign):
        scalar_vars = []
        list_var = None
        for var in assign:
            if not is_var(var):
                raise DataError('Invalid variable to assign: %s' % var)
            if list_var:
                raise DataError('Only the last variable to assign can be '
                                'a list variable.')
            if is_list_var(var):
                list_var = var
            else:
                scalar_vars.append(var)
        return scalar_vars, list_var

    def __len__(self):
        return len(self.scalar_vars) + (1 if self.list_var else 0)

    def __iter__(self):
        for var in self.scalar_vars:
            yield var
        if self.list_var:
            yield self.list_var

    def set_variables(self, context, return_value):
        if not self:
            return
        if self._error:
            raise self._error
        for name, value in self._get_vars_to_set(return_value):
            context.get_current_vars()[name] = value
            if is_list_var(name) or utils.is_list(value):
                value = utils.seq2str2(value)
            else:
                value = utils.unic(value)
            context.output.info('%s = %s' % (name, utils.cut_long_assign_msg(value)))

    def _get_vars_to_set(self, ret):
        if ret is None:
            return self._get_vars_to_set_when_ret_is_none()
        if not self.list_var:
            return self._get_vars_to_set_with_only_scalars(ret)
        if self._is_non_string_iterable(ret):
            return self._get_vars_to_set_with_scalars_and_list(list(ret))
        self._raise_invalid_return_value(ret, wrong_type=True)

    def _is_non_string_iterable(self, value):
        if isinstance(value, basestring):
            return False
        try:
            iter(value)
        except TypeError:
            return False
        else:
            return True

    def _get_vars_to_set_when_ret_is_none(self):
        ret = [ (var, None) for var in self.scalar_vars ]
        if self.list_var:
            ret.append((self.list_var, []))
        return ret

    def _get_vars_to_set_with_only_scalars(self, ret):
        needed = len(self.scalar_vars)
        if needed == 1:
            return [(self.scalar_vars[0], ret)]
        if not self._is_non_string_iterable(ret):
            self._raise_invalid_return_value(ret, wrong_type=True)
        ret = list(ret)
        if len(ret) < needed:
            self._raise_invalid_return_value(ret)
        if len(ret) == needed:
            return zip(self.scalar_vars, ret)
        return zip(self.scalar_vars[:-1], ret) \
                    + [(self.scalar_vars[-1], ret[needed-1:])]

    def _get_vars_to_set_with_scalars_and_list(self, ret):
        needed_scalars = len(self.scalar_vars)
        if needed_scalars == 0:
            return [(self.list_var, ret)]
        if len(ret) < needed_scalars:
            self._raise_invalid_return_value(ret)
        return zip(self.scalar_vars, ret) \
                    + [(self.list_var, ret[needed_scalars:])]

    def _raise_invalid_return_value(self, ret, wrong_type=False):
        if wrong_type:
            err = 'Expected list like object, got %s instead' % utils.type_as_str(ret, True)
        else:
            err = 'Need more values than %d' % len(ret)
        raise DataError("Cannot assign return value of keyword '%s' to variable%s %s: %s" 
                        % (self.keyword, utils.plural_or_not(len(self)),
                           utils.seq2str(list(self)), err))


class ForLoop(BaseKeyword):

    def __init__(self, forstep):
        BaseKeyword.__init__(self, self._get_name(forstep), type='for')
        self.vars = forstep.vars
        self.items = forstep.items
        self.range = forstep.range
        self.keywords = Keywords(forstep.steps)

    def _get_name(self, data):
        return '%s %s [ %s ]' % (' | '.join(data.vars),
                                 'IN' if not data.range else 'IN RANGE',
                                 ' | '.join(data.items))

    def run(self, context):
        self.starttime = utils.get_timestamp()
        context.output.start_keyword(self)
        try:
            self._validate_vars()
            self._run(context)
        except ExecutionFailed, err:
            error = err
        except DataError, err:
            msg = unicode(err)
            context.output.fail(msg)
            error = ExecutionFailed(msg, syntax=True)
        else:
            error = None
        self.status = 'PASS' if not error else 'FAIL'
        self.endtime = utils.get_timestamp()
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)
        context.output.end_keyword(self)
        if error:
            raise error

    def _validate_vars(self):
        if not self.vars:
            raise DataError('FOR loop variables missing.')
        for var in self.vars:
            if not is_scalar_var(var):
                raise DataError("Invalid FOR loop variable '%s'." % var)

    def _run(self, context):
        errors = []
        items, iteration_steps = self._get_items_and_iteration_steps(context)
        for i in iteration_steps:
            values = items[i:i+len(self.vars)]
            err = self._run_one_round(context, self.vars, values)
            if err:
                errors.extend(err.get_errors())
                if not err.cont:
                    break
        if errors:
            raise ExecutionFailures(errors)

    def _get_items_and_iteration_steps(self, context):
        if context.dry_run:
            return self.vars, [0]
        items = self._replace_vars_from_items(context.get_current_vars())
        return items, range(0, len(items), len(self.vars))

    def _run_one_round(self, context, variables, values):
        foritem = _ForItem(variables, values)
        context.output.start_keyword(foritem)
        for var, value in zip(variables, values):
            context.get_current_vars()[var] = value
        try:
            self.keywords.run(context)
        except ExecutionFailed, err:
            error = err
        else:
            error = None
        foritem.end('PASS' if not error else 'FAIL')
        context.output.end_keyword(foritem)
        return error

    def _replace_vars_from_items(self, variables):
        items = variables.replace_list(self.items)
        if self.range:
            items = self._get_range_items(items)
        if len(items) % len(self.vars) == 0:
            return items
        raise DataError('Number of FOR loop values should be multiple of '
                        'variables. Got %d variables (%s) but %d value%s.'
                        % (len(self.vars), utils.seq2str(self.vars),
                           len(items), utils.plural_or_not(items)))

    def _get_range_items(self, items):
        try:
            items = [ int(item) for item in items ]
        except:
            raise DataError('Converting argument of FOR IN RANGE failed: %s'
                            % utils.get_error_message())
        if not 1 <= len(items) <= 3:
            raise DataError('FOR IN RANGE expected 1-3 arguments, '
                            'got %d instead.' % len(items))
        return range(*items)


class _ForItem(BaseKeyword):

    def __init__(self, vars, items):
        name = ', '.join('%s = %s' % (var, utils.cut_long_assign_msg(item))
                         for var, item in zip(vars, items))
        BaseKeyword.__init__(self, name, type='foritem')
        self.starttime = utils.get_timestamp()

    def end(self, status):
        self.status = status
        self.endtime = utils.get_timestamp()
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)
