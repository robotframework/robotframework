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
                          ExitForLoop, ContinueForLoop, DataError)
from robot.result import Keyword as KeywordResult
from robot.output import librarylogger as logger
from robot.utils import (format_assign_message, frange, get_error_message,
                         is_list_like, is_number, plural_or_not as s,
                         split_from_equals, type_name, is_unicode)
from robot.variables import is_dict_variable, evaluate_expression

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
        if step.type == step.IF_TYPE:
            runner = IfRunner(context, self._templated)
            return runner.run(step)
        runner = context.get_runner(name or step.name)
        if context.dry_run:
            return runner.dry_run(step, context)
        return runner.run(step, context)


class IfRunner(object):
    _dry_run_stack = []

    def __init__(self, context, templated=False):
        self._context = context
        self._templated = templated

    def run(self, data, name=None):
        branch_run = False
        with self._dry_run_recursion_detection(data) as recursive_dry_run:
            while data:
                branch_run = self._run_if_branch(data, branch_run, recursive_dry_run)
                data = data.orelse

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

    def _run_if_branch(self, data, branch_run=False, recursive_dry_run=False):
        result = KeywordResult(kwname=data.condition, type=data.type,
                               lineno=data.lineno, source=data.source)
        with StatusReporter(self._context, result) as reporter:
            if data.error:
                raise DataError(data.error)
            if self._should_run_branch(data.condition, branch_run, recursive_dry_run):
                runner = StepRunner(self._context, self._templated)
                runner.run_steps(data.keywords)
                return True
            reporter.mark_as_not_run()
            return branch_run

    def _should_run_branch(self, condition, branch_run=False, recursive_dry_run=False):
        if self._context.dry_run:
            return not recursive_dry_run
        if branch_run:
            return False
        if condition is None:
            return True
        condition = self._context.variables.replace_scalar(condition)
        if is_unicode(condition):
            return evaluate_expression(condition, self._context.variables.current.store)
        return bool(condition)


def ForRunner(context, templated=False, flavor='IN'):
    runners = {'IN': ForInRunner,
               'IN RANGE': ForInRangeRunner,
               'IN ZIP': ForInZipRunner,
               'IN ENUMERATE': ForInEnumerateRunner}
    runner = runners[flavor or 'IN']
    return runner(context, templated)


class ForInRunner(object):
    flavor = 'IN'

    def __init__(self, context, templated=False):
        self._context = context
        self._templated = templated

    def run(self, data, name=None):
        result = KeywordResult(kwname=self._get_name(data),
                               type=data.FOR_LOOP_TYPE,
                               lineno=data.lineno,
                               source=data.source)
        with StatusReporter(self._context, result):
            if data.error:
                raise DataError(data.error)
            self._run(data)

    def _get_name(self, data):
        return '%s %s [ %s ]' % (' | '.join(data.variables),
                                 self.flavor,
                                 ' | '.join(data.values))

    def _run(self, data):
        errors = []
        for values in self._get_values_for_rounds(data):
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

    def _get_values_for_rounds(self, data):
        values_per_round = len(data.variables)
        if self._context.dry_run:
            return ForInRunner._map_values_to_rounds(
                self, data.variables, values_per_round
            )
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

    def _run_one_round(self, data, values):
        variables = self._map_variables_and_values(data.variables, values)
        for name, value in variables:
            self._context.variables[name] = value
        name = ', '.join(format_assign_message(n, v) for n, v in variables)
        result = KeywordResult(kwname=name,
                               type=data.FOR_ITEM_TYPE,
                               lineno=data.lineno,
                               source=data.source)
        runner = StepRunner(self._context, self._templated)
        with StatusReporter(self._context, result):
            runner.run_steps(data.keywords)

    def _map_variables_and_values(self, variables, values):
        if len(variables) == 1 and len(values) != 1:
            return [(variables[0], tuple(values))]
        return list(zip(variables, values))


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
