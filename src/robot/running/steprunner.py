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

from robot.errors import (ExecutionFailed, ExecutionFailures, ExecutionPassed,
                          ExitForLoop, ContinueForLoop, DataError)
from robot.result import Keyword as KeywordResult
from robot.utils import (format_assign_message, frange, get_error_message,
                         is_list_like, is_number, plural_or_not as s, type_name)
from robot.variables import is_scalar_var

from .statusreporter import StatusReporter


class StepRunner(object):

    def __init__(self, context, templated=False):
        self._context = context
        self._templated = bool(templated)

    def run_steps(self, steps):
        errors = []
        for step in steps:
            try:
                self.run_step(step)
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

    def run_step(self, step, name=None):
        context = self._context
        if step.type == step.FOR_LOOP_TYPE:
            runner = ForRunner(context, self._templated, step.flavor)
            return runner.run(step)
        runner = context.get_runner(name or step.name)
        if context.dry_run:
            return runner.dry_run(step, context)
        return runner.run(step, context)


def ForRunner(context, templated=False, flavor='IN'):
    runners = {'IN': ForInRunner,
               'IN RANGE': ForInRangeRunner,
               'IN ZIP': ForInZipRunner,
               'IN ENUMERATE': ForInEnumerateRunner}
    try:
        runner = runners[flavor]
    except KeyError:
        return InvalidForRunner(context, flavor)
    return runner(context, templated)


class ForInRunner(object):

    def __init__(self, context, templated=False):
        self._context = context
        self._templated = templated

    def run(self, data, name=None):
        result = KeywordResult(kwname=self._get_name(data),
                               type=data.FOR_LOOP_TYPE)
        with StatusReporter(self._context, result):
            self._validate(data)
            self._run(data)

    def _get_name(self, data):
        return '%s %s [ %s ]' % (' | '.join(data.variables),
                                 self._flavor_name(),
                                 ' | '.join(data.values))

    def _flavor_name(self):
        return 'IN'

    def _validate(self, data):
        if not data.variables:
            raise DataError('FOR loop has no loop variables.')
        for var in data.variables:
            if not is_scalar_var(var):
                raise DataError("Invalid FOR loop variable '%s'." % var)
        if not data.values:
            raise DataError('FOR loop has no loop values.')
        if not data.keywords:
            raise DataError('FOR loop contains no keywords.')

    def _run(self, data):
        errors = []
        for values in self._get_values_for_one_round(data):
            try:
                self._run_one_round(data, values)
            except ExitForLoop as exception:
                if exception.earlier_failures:
                    errors.extend(exception.earlier_failures.get_errors())
                break
            except ContinueForLoop as exception:
                if exception.earlier_failures:
                    errors.extend(exception.earlier_failures.get_errors())
                continue
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

    def _get_values_for_one_round(self, data):
        if not self._context.dry_run:
            values = self._replace_variables(data)
            var_count = self._values_per_iteration(data.variables)
            for i in range(0, len(values), var_count):
                yield values[i:i+var_count]
        else:
            yield data.variables

    def _replace_variables(self, data):
        values = self._context.variables.replace_list(data.values)
        values = self._transform_items(values)
        values_per_iteration = self._values_per_iteration(data.variables)
        if len(values) % values_per_iteration == 0:
            return values
        self._raise_wrong_variable_count(values_per_iteration, len(values))

    def _raise_wrong_variable_count(self, variables, values):
        raise DataError('Number of FOR loop values should be multiple of '
                        'its variables. Got %d variables but %d value%s.'
                        % (variables, values, s(values)))

    def _run_one_round(self, data, values):
        name = ', '.join(format_assign_message(var, item)
                         for var, item in zip(data.variables, values))
        result = KeywordResult(kwname=name,
                               type=data.FOR_ITEM_TYPE)
        for var, value in zip(data.variables, values):
            self._context.variables[var] = value
        runner = StepRunner(self._context, self._templated)
        with StatusReporter(self._context, result):
            runner.run_steps(data.keywords)

    def _transform_items(self, items):
        return items

    def _values_per_iteration(self, variables):
        """
        The number of values per iteration;
        used to check if we have (a multiple of this) values.

        This is its own method to support loops like ForInEnumerate
        which add/remove items to the pool.
        """
        return len(variables)


class ForInRangeRunner(ForInRunner):

    def __init__(self, context, templated=False):
        super(ForInRangeRunner, self).__init__(context, templated)

    def _flavor_name(self):
        return 'IN RANGE'

    def _transform_items(self, items):
        try:
            items = [self._to_number_with_arithmetics(item) for item in items]
        except:
            raise DataError('Converting argument of FOR IN RANGE failed: %s.'
                            % get_error_message())
        if not 1 <= len(items) <= 3:
            raise DataError('FOR IN RANGE expected 1-3 arguments, got %d.'
                            % len(items))
        return frange(*items)

    def _to_number_with_arithmetics(self, item):
        if is_number(item):
            return item
        number = eval(str(item), {})
        if not is_number(number):
            raise TypeError("Expected number, got %s." % type_name(item))
        return number


class ForInZipRunner(ForInRunner):

    def __init__(self, context, templated=False):
        super(ForInZipRunner, self).__init__(context, templated)

    def _flavor_name(self):
        return 'IN ZIP'

    def _replace_variables(self, data):
        values = super(ForInZipRunner, self)._replace_variables(data)
        if len(data.variables) == len(data.values):
            return values
        raise DataError('FOR IN ZIP expects an equal number of variables and '
                        'iterables. Got %d variable%s and %d iterable%s.'
                        % (len(data.variables), s(data.variables),
                           len(data.values), s(data.values)))

    def _transform_items(self, items):
        answer = list()
        for item in items:
            if not is_list_like(item):
                raise DataError('FOR IN ZIP items must all be list-like, '
                                'got %s.' % type_name(item))
        for zipped_item in zip(*[list(item) for item in items]):
            answer.extend(zipped_item)
        return answer


class ForInEnumerateRunner(ForInRunner):

    def __init__(self, context, templated=False):
        super(ForInEnumerateRunner, self).__init__(context, templated)

    def _flavor_name(self):
        return 'IN ENUMERATE'

    def _values_per_iteration(self, variables):
        if len(variables) < 2:
            raise DataError('FOR IN ENUMERATE expected 2 or more loop '
                            'variables, got %d.' % len(variables))
        return len(variables) - 1

    def _get_values_for_one_round(self, data):
        parent = super(ForInEnumerateRunner, self)
        for index, values in enumerate(parent._get_values_for_one_round(data)):
            yield [index] + values

    def _raise_wrong_variable_count(self, variables, values):
        raise DataError('Number of FOR IN ENUMERATE loop values should be '
                        'multiple of its variables (excluding the index). '
                        'Got %d variable%s but %d value%s.'
                        % (variables, s(variables), values, s(values)))


class InvalidForRunner(ForInRunner):
    """Used to send an error from ForRunner() if it sees an unexpected error.

    We can't simply throw a DataError from ForRunner() because that happens
    outside the "with StatusReporter(...)" blocks.
    """

    def __init__(self, context, flavor):
        super(InvalidForRunner, self).__init__(context, False)
        self.flavor = flavor

    def _run(self, data, *args, **kwargs):
        raise DataError("Invalid FOR loop type '%s'. Expected 'IN', "
                        "'IN RANGE', 'IN ZIP', or 'IN ENUMERATE'."
                        % self.flavor)
