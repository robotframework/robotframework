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

from collections import OrderedDict
from contextlib import contextmanager

from robot.errors import (ExecutionFailed, ExecutionFailures, ExecutionPassed,
                          ExecutionStatus, ExitForLoop, ContinueForLoop, DataError)
from robot.result import For as ForResult, If as IfResult, IfBranch as IfBranchResult
from robot.output import librarylogger as logger
from robot.utils import (cut_assign_value, frange, get_error_message,
                         is_list_like, is_number, is_unicode, plural_or_not as s,
                         split_from_equals, type_name)
from robot.variables import is_dict_variable, evaluate_expression

from .statusreporter import StatusReporter


class BodyRunner(object):

    def __init__(self, context, run=True, templated=False):
        self._context = context
        self._run = run
        self._templated = templated

    def run(self, body):
        errors = []
        for step in body:
            try:
                step.run(self._context, self._run, self._templated)
            except ExecutionPassed as exception:
                exception.set_earlier_failures(errors)
                raise exception
            except ExecutionFailed as exception:
                errors.extend(exception.get_errors())
                self._run = exception.can_continue(self._context,
                                                   self._templated)
        if errors:
            raise ExecutionFailures(errors)


class KeywordRunner(object):

    def __init__(self, context, run=True):
        self._context = context
        self._run = run

    def run(self, step, name=None):
        context = self._context
        runner = context.get_runner(name or step.name)
        if context.dry_run:
            return runner.dry_run(step, context)
        return runner.run(step, context, self._run)


class IfRunner(object):
    _dry_run_stack = []

    def __init__(self, context, run=True, templated=False):
        self._context = context
        self._run = run
        self._templated = templated

    def run(self, data):
        with self._dry_run_recursion_detection(data) as recursive_dry_run:
            error = None
            with StatusReporter(data, IfResult(), self._context, self._run):
                for branch in data.body:
                    try:
                        if self._run_if_branch(branch, recursive_dry_run, data.error):
                            self._run = False
                    except ExecutionStatus as err:
                        error = err
                        self._run = False
                if error:
                    raise error

    @contextmanager
    def _dry_run_recursion_detection(self, data):
        dry_run = self._context.dry_run
        if dry_run:
            recursive_dry_run = data in self._dry_run_stack
            self._dry_run_stack.append(data)
        else:
            recursive_dry_run = False
        try:
            yield recursive_dry_run
        finally:
            if dry_run:
                self._dry_run_stack.pop()

    def _run_if_branch(self, branch, recursive_dry_run=False, error=None):
        result = IfBranchResult(branch.type, branch.condition)
        try:
            run_branch = self._should_run_branch(branch.condition, recursive_dry_run)
        except:
            error = get_error_message()
            run_branch = False
        with StatusReporter(branch, result, self._context, run_branch):
            if error and self._run:
                raise DataError(error)
            runner = BodyRunner(self._context, run_branch, self._templated)
            if not recursive_dry_run:
                runner.run(branch.body)
        return run_branch

    def _should_run_branch(self, condition, recursive_dry_run=False):
        if self._context.dry_run:
            return not recursive_dry_run
        if not self._run:
            return False
        if condition is None:
            return True
        condition = self._context.variables.replace_scalar(condition)
        if is_unicode(condition):
            return evaluate_expression(condition, self._context.variables.current.store)
        return bool(condition)


def ForRunner(context, flavor='IN', run=True, templated=False):
    runners = {'IN': ForInRunner,
               'IN RANGE': ForInRangeRunner,
               'IN ZIP': ForInZipRunner,
               'IN ENUMERATE': ForInEnumerateRunner}
    runner = runners[flavor or 'IN']
    return runner(context, run, templated)


class ForInRunner(object):
    flavor = 'IN'

    def __init__(self, context, run=True, templated=False):
        self._context = context
        self._run = run
        self._templated = templated

    def run(self, data):
        result = ForResult(data.variables, data.flavor, data.values)
        with StatusReporter(data, result, self._context, self._run):
            if self._run:
                if data.error:
                    raise DataError(data.error)
                self._run_loop(data, result)
            else:
                self._run_one_round(data, result)

    def _run_loop(self, data, result):
        errors = []
        for values in self._get_values_for_rounds(data):
            try:
                self._run_one_round(data, result, values)
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
                if not exception.can_continue(self._context,
                                              self._templated):
                    break
        if errors:
            raise ExecutionFailures(errors)

    def _get_values_for_rounds(self, data):
        if self._context.dry_run:
            return [None]
        values_per_round = len(data.variables)
        if self._is_dict_iteration(data.values):
            values = self._resolve_dict_values(data.values)
            values = self._map_dict_values_to_rounds(values, values_per_round)
        else:
            values = self._resolve_values(data.values)
            values = self._map_values_to_rounds(values, values_per_round)
        return values

    def _is_dict_iteration(self, values):
        all_name_value = True
        for item in values:
            if is_dict_variable(item):
                return True
            if split_from_equals(item)[1] is None:
                all_name_value = False
        if all_name_value:
            name, value = split_from_equals(values[0])
            logger.warn(
                "FOR loop iteration over values that are all in 'name=value' "
                "format like '%s' is deprecated. In the future this syntax "
                "will mean iterating over names and values separately like "
                "when iterating over '&{dict} variables. Escape at least one "
                "of the values like '%s\\=%s' to use normal FOR loop "
                "iteration and to disable this warning."
                % (values[0], name, value)
            )
        return False

    def _resolve_dict_values(self, values):
        result = OrderedDict()
        replace_scalar = self._context.variables.replace_scalar
        for item in values:
            if is_dict_variable(item):
                result.update(replace_scalar(item))
            else:
                key, value = split_from_equals(item)
                if value is None:
                    raise DataError(
                        "Invalid FOR loop value '%s'. When iterating over "
                        "dictionaries, values must be '&{dict}' variables "
                        "or use 'key=value' syntax." % item
                    )
                try:
                    result[replace_scalar(key)] = replace_scalar(value)
                except TypeError:
                    raise DataError(
                        "Invalid dictionary item '%s': %s"
                        % (item, get_error_message())
                    )
        return result.items()

    def _map_dict_values_to_rounds(self, values, per_round):
        if per_round > 2:
            raise DataError(
                'Number of FOR loop variables must be 1 or 2 when iterating '
                'over dictionaries, got %d.' % per_round
            )
        return values

    def _resolve_values(self, values):
        return self._context.variables.replace_list(values)

    def _map_values_to_rounds(self, values, per_round):
        count = len(values)
        if count % per_round != 0:
            self._raise_wrong_variable_count(per_round, count)
        # Map list of values to list of lists containing values per round.
        return (values[i:i+per_round] for i in range(0, count, per_round))

    def _raise_wrong_variable_count(self, variables, values):
        raise DataError(
            'Number of FOR loop values should be multiple of its variables. '
            'Got %d variables but %d value%s.' % (variables, values, s(values))
        )

    def _run_one_round(self, data, result, values=None):
        result = result.body.create_iteration()
        variables = self._map_variables_and_values(data.variables, values)
        for name, value in variables:
            self._context.variables[name] = value
            result.variables[name] = cut_assign_value(value)
        runner = BodyRunner(self._context, self._run, self._templated)
        with StatusReporter(data, result, self._context, self._run):
            runner.run(data.body)

    def _map_variables_and_values(self, variables, values):
        if values is None:    # Failure occurred earlier or dry-run.
            values = variables
        if len(variables) == 1 and len(values) != 1:
            return [(variables[0], tuple(values))]
        return zip(variables, values)


class ForInRangeRunner(ForInRunner):
    flavor = 'IN RANGE'

    def _resolve_dict_values(self, values):
        raise DataError(
            'FOR IN RANGE loops do not support iterating over dictionaries.'
        )

    def _map_values_to_rounds(self, values, per_round):
        if not 1 <= len(values) <= 3:
            raise DataError(
                'FOR IN RANGE expected 1-3 values, got %d.' % len(values)
            )
        try:
            values = [self._to_number_with_arithmetic(v) for v in values]
        except:
            raise DataError(
                'Converting FOR IN RANGE values failed: %s.'
                % get_error_message()
            )
        values = frange(*values)
        return ForInRunner._map_values_to_rounds(self, values, per_round)

    def _to_number_with_arithmetic(self, item):
        if is_number(item):
            return item
        number = eval(str(item), {})
        if not is_number(number):
            raise TypeError("Expected number, got %s." % type_name(item))
        return number


class ForInZipRunner(ForInRunner):
    flavor = 'IN ZIP'
    _start = 0

    def _resolve_dict_values(self, values):
        raise DataError(
            'FOR IN ZIP loops do not support iterating over dictionaries.'
        )

    def _map_values_to_rounds(self, values, per_round):
        for item in values:
            if not is_list_like(item):
                raise DataError(
                    "FOR IN ZIP items must all be list-like, got %s '%s'."
                    % (type_name(item), item)
                )
        if len(values) % per_round != 0:
            self._raise_wrong_variable_count(per_round, len(values))
        return zip(*(list(item) for item in values))


class ForInEnumerateRunner(ForInRunner):
    flavor = 'IN ENUMERATE'

    def _resolve_dict_values(self, values):
        self._start, values = self._get_start(values)
        return ForInRunner._resolve_dict_values(self, values)

    def _resolve_values(self, values):
        self._start, values = self._get_start(values)
        return ForInRunner._resolve_values(self, values)

    def _get_start(self, values):
        if not values[-1].startswith('start='):
            return 0, values
        start = self._context.variables.replace_string(values[-1][6:])
        if len(values) == 1:
            raise DataError('FOR loop has no loop values.')
        try:
            return int(start), values[:-1]
        except ValueError:
            raise ValueError("Invalid FOR IN ENUMERATE start value '%s'." % start)

    def _map_dict_values_to_rounds(self, values, per_round):
        if per_round > 3:
            raise DataError(
                'Number of FOR IN ENUMERATE loop variables must be 1-3 when '
                'iterating over dictionaries, got %d.' % per_round
            )
        if per_round == 2:
            return ((i, v) for i, v in enumerate(values, start=self._start))
        return ((i,) + v for i, v in enumerate(values, start=self._start))

    def _map_values_to_rounds(self, values, per_round):
        per_round = max(per_round-1, 1)
        values = ForInRunner._map_values_to_rounds(self, values, per_round)
        return ([i] + v for i, v in enumerate(values, start=self._start))

    def _raise_wrong_variable_count(self, variables, values):
        raise DataError(
            'Number of FOR IN ENUMERATE loop values should be multiple of '
            'its variables (excluding the index). Got %d variables but %d '
            'value%s.' % (variables, values, s(values))
        )
