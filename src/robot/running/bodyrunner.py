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
from itertools import zip_longest
import re
import time

from robot.errors import (BreakLoop, ContinueLoop, DataError, ExecutionFailed,
                          ExecutionFailures, ExecutionPassed, ExecutionStatus)
from robot.result import (For as ForResult, While as WhileResult, If as IfResult,
                          IfBranch as IfBranchResult, Try as TryResult,
                          TryBranch as TryBranchResult)
from robot.output import librarylogger as logger
from robot.utils import (cut_assign_value, frange, get_error_message, get_timestamp,
                         is_list_like, is_number, plural_or_not as s, secs_to_timestr,
                         seq2str, split_from_equals, type_name, Matcher, timestr_to_secs)
from robot.variables import is_dict_variable, evaluate_expression

from .statusreporter import StatusReporter


DEFAULT_WHILE_LIMIT = 10_000


class BodyRunner:

    def __init__(self, context, run=True, templated=False):
        self._context = context
        self._run = run
        self._templated = templated

    def run(self, body):
        errors = []
        passed = None
        for step in body:
            try:
                step.run(self._context, self._run, self._templated)
            except ExecutionPassed as exception:
                exception.set_earlier_failures(errors)
                passed = exception
                self._run = False
            except ExecutionFailed as exception:
                errors.extend(exception.get_errors())
                self._run = exception.can_continue(self._context, self._templated)
        if passed:
            raise passed
        if errors:
            raise ExecutionFailures(errors)


class KeywordRunner:

    def __init__(self, context, run=True):
        self._context = context
        self._run = run

    def run(self, step, name=None):
        context = self._context
        runner = context.get_runner(name or step.name)
        if context.dry_run:
            return runner.dry_run(step, context)
        return runner.run(step, context, self._run)


def ForRunner(context, flavor='IN', run=True, templated=False):
    runners = {'IN': ForInRunner,
               'IN RANGE': ForInRangeRunner,
               'IN ZIP': ForInZipRunner,
               'IN ENUMERATE': ForInEnumerateRunner}
    runner = runners[flavor or 'IN']
    return runner(context, run, templated)


class ForInRunner:
    flavor = 'IN'

    def __init__(self, context, run=True, templated=False):
        self._context = context
        self._run = run
        self._templated = templated

    def run(self, data):
        error = None
        run = False
        if self._run:
            if data.error:
                error = DataError(data.error, syntax=True)
            else:
                run = True
        result = ForResult(data.variables, data.flavor, data.values, data.start,
                           data.mode, data.fill)
        with StatusReporter(data, result, self._context, run) as status:
            if run:
                try:
                    values_for_rounds = self._get_values_for_rounds(data)
                except DataError as err:
                    error = err
                else:
                    if self._run_loop(data, result, values_for_rounds):
                        return
            status.pass_status = result.NOT_RUN
            self._run_one_round(data, result, run=False)
            if error:
                raise error

    def _run_loop(self, data, result, values_for_rounds):
        errors = []
        executed = False
        for values in values_for_rounds:
            executed = True
            try:
                self._run_one_round(data, result, values)
            except (BreakLoop, ContinueLoop) as ctrl:
                if ctrl.earlier_failures:
                    errors.extend(ctrl.earlier_failures.get_errors())
                if isinstance(ctrl, BreakLoop):
                    break
            except ExecutionPassed as passed:
                passed.set_earlier_failures(errors)
                raise passed
            except ExecutionFailed as failed:
                errors.extend(failed.get_errors())
                if not failed.can_continue(self._context, self._templated):
                    break
        if errors:
            raise ExecutionFailures(errors)
        return executed

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
        if all_name_value and values:
            name, value = split_from_equals(values[0])
            logger.warn(
                f"FOR loop iteration over values that are all in 'name=value' "
                f"format like '{values[0]}' is deprecated. In the future this syntax "
                f"will mean iterating over names and values separately like "
                f"when iterating over '&{{dict}} variables. Escape at least one "
                f"of the values like '{name}\\={value}' to use normal FOR loop "
                f"iteration and to disable this warning."
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
                    raise DataError(f"Invalid FOR loop value '{item}'. When iterating "
                                    f"over dictionaries, values must be '&{{dict}}' "
                                    f"variables or use 'key=value' syntax.", syntax=True)
                try:
                    result[replace_scalar(key)] = replace_scalar(value)
                except TypeError:
                    err = get_error_message()
                    raise DataError(f"Invalid dictionary item '{item}': {err}")
        return result.items()

    def _map_dict_values_to_rounds(self, values, per_round):
        if per_round > 2:
            raise DataError(f'Number of FOR loop variables must be 1 or 2 when '
                            f'iterating over dictionaries, got {per_round}.',
                            syntax=True)
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
        raise DataError(f'Number of FOR loop values should be multiple of its '
                        f'variables. Got {variables} variables but {values} '
                        f'value{s(values)}.')

    def _run_one_round(self, data, result, values=None, run=True):
        result = result.body.create_iteration()
        if values is not None:
            variables = self._context.variables
        else:    # Not really run (earlier failure, unexecuted IF branch, dry-run)
            variables = {}
            values = [''] * len(data.variables)
        for name, value in self._map_variables_and_values(data.variables, values):
            variables[name] = value
            result.variables[name] = cut_assign_value(value)
        runner = BodyRunner(self._context, run, self._templated)
        with StatusReporter(data, result, self._context, run):
            runner.run(data.body)

    def _map_variables_and_values(self, variables, values):
        if len(variables) == 1 and len(values) != 1:
            return [(variables[0], tuple(values))]
        return zip(variables, values)


class ForInRangeRunner(ForInRunner):
    flavor = 'IN RANGE'

    def _resolve_dict_values(self, values):
        raise DataError('FOR IN RANGE loops do not support iterating over '
                        'dictionaries.', syntax=True)

    def _map_values_to_rounds(self, values, per_round):
        if not 1 <= len(values) <= 3:
            raise DataError(f'FOR IN RANGE expected 1-3 values, got {len(values)}.',
                            syntax=True)
        try:
            values = [self._to_number_with_arithmetic(v) for v in values]
        except Exception:
            msg = get_error_message()
            raise DataError(f'Converting FOR IN RANGE values failed: {msg}.')
        values = frange(*values)
        return super()._map_values_to_rounds(values, per_round)

    def _to_number_with_arithmetic(self, item):
        if is_number(item):
            return item
        number = eval(str(item), {})
        if not is_number(number):
            raise TypeError(f'Expected number, got {type_name(item)}.')
        return number


class ForInZipRunner(ForInRunner):
    flavor = 'IN ZIP'
    _mode = None
    _fill = None

    def _get_values_for_rounds(self, data):
        self._mode = self._resolve_mode(data.mode)
        self._fill = self._resolve_fill(data.fill)
        return super()._get_values_for_rounds(data)

    def _resolve_mode(self, mode):
        if not mode or self._context.dry_run:
            return None
        try:
            mode = self._context.variables.replace_string(mode).upper()
            if mode in ('STRICT', 'SHORTEST', 'LONGEST'):
                return mode
            raise DataError(f"Mode must be 'STRICT', 'SHORTEST' or 'LONGEST', "
                            f"got '{mode}'.")
        except DataError as err:
            raise DataError(f'Invalid mode: {err}')

    def _resolve_fill(self, fill):
        if not fill or self._context.dry_run:
            return None
        try:
            return self._context.variables.replace_scalar(fill)
        except DataError as err:
            raise DataError(f'Invalid fill value: {err}')

    def _resolve_dict_values(self, values):
        raise DataError('FOR IN ZIP loops do not support iterating over dictionaries.',
                        syntax=True)

    def _map_values_to_rounds(self, values, per_round):
        self._validate_types(values)
        if len(values) % per_round != 0:
            self._raise_wrong_variable_count(per_round, len(values))
        if self._mode == 'LONGEST':
            return zip_longest(*values, fillvalue=self._fill)
        if self._mode == 'STRICT':
            self._validate_strict_lengths(values)
        return zip(*values)

    def _validate_types(self, values):
        for index, item in enumerate(values, start=1):
            if not is_list_like(item):
                raise DataError(f"FOR IN ZIP items must be list-like, but item {index} "
                                f"is {type_name(item)}.")

    def _validate_strict_lengths(self, values):
        lengths = []
        for index, item in enumerate(values, start=1):
            try:
                lengths.append(len(item))
            except TypeError:
                raise DataError(f"FOR IN ZIP items should have length in STRICT mode, "
                                f"but item {index} does not.")
        if len(set(lengths)) > 1:
            raise DataError(f"FOR IN ZIP items should have equal lengths in STRICT "
                            f"mode, but lengths are {seq2str(lengths, quote='')}.")


class ForInEnumerateRunner(ForInRunner):
    flavor = 'IN ENUMERATE'
    _start = 0

    def _get_values_for_rounds(self, data):
        self._start = self._resolve_start(data.start)
        return super()._get_values_for_rounds(data)

    def _resolve_start(self, start):
        if not start or self._context.dry_run:
            return 0
        try:
            start = self._context.variables.replace_string(start)
            try:
                return int(start)
            except ValueError:
                raise DataError(f"Start value must be an integer, got '{start}'.")
        except DataError as err:
            raise DataError(f'Invalid start value: {err}')

    def _map_dict_values_to_rounds(self, values, per_round):
        if per_round > 3:
            raise DataError(f'Number of FOR IN ENUMERATE loop variables must be 1-3 '
                            f'when iterating over dictionaries, got {per_round}.',
                            syntax=True)
        if per_round == 2:
            return ((i, v) for i, v in enumerate(values, start=self._start))
        return ((i,) + v for i, v in enumerate(values, start=self._start))

    def _map_values_to_rounds(self, values, per_round):
        per_round = max(per_round-1, 1)
        values = super()._map_values_to_rounds(values, per_round)
        return ([i] + v for i, v in enumerate(values, start=self._start))

    def _raise_wrong_variable_count(self, variables, values):
        raise DataError(f'Number of FOR IN ENUMERATE loop values should be multiple of '
                        f'its variables (excluding the index). Got {variables} '
                        f'variables but {values} value{s(values)}.')


class WhileRunner:

    def __init__(self, context, run=True, templated=False):
        self._context = context
        self._run = run
        self._templated = templated

    def run(self, data):
        ctx = self._context
        error = None
        run = False
        limit = None
        loop_result = WhileResult(data.condition, data.limit,
                                  data.on_limit, data.on_limit_message,
                                  starttime=get_timestamp())
        iter_result = loop_result.body.create_iteration(starttime=get_timestamp())
        if self._run:
            if data.error:
                error = DataError(data.error, syntax=True)
            elif not ctx.dry_run:
                try:
                    limit = WhileLimit.create(data.limit,
                                              data.on_limit,
                                              data.on_limit_message,
                                              ctx.variables)
                    run = self._should_run(data.condition, ctx.variables)
                except DataError as err:
                    error = err
        with StatusReporter(data, loop_result, self._context, run):
            if ctx.dry_run or not run:
                self._run_iteration(data, iter_result, run)
                if error:
                    raise error
                return
            errors = []
            while True:
                try:
                    with limit:
                        self._run_iteration(data, iter_result)
                except (BreakLoop, ContinueLoop) as ctrl:
                    if ctrl.earlier_failures:
                        errors.extend(ctrl.earlier_failures.get_errors())
                    if isinstance(ctrl, BreakLoop):
                        break
                except ExecutionPassed as passed:
                    passed.set_earlier_failures(errors)
                    raise passed
                except LimitExceeded as exceeded:
                    if exceeded.on_limit_pass:
                        self._context.info(exceeded.message)
                    else:
                        errors.append(exceeded)
                    break
                except ExecutionFailed as failed:
                    errors.extend(failed.get_errors())
                    if not failed.can_continue(ctx, self._templated):
                        break
                iter_result = loop_result.body.create_iteration(starttime=get_timestamp())
                if not self._should_run(data.condition, ctx.variables):
                    break
            if errors:
                raise ExecutionFailures(errors)

    def _run_iteration(self, data, result, run=True):
        runner = BodyRunner(self._context, run, self._templated)
        with StatusReporter(data, result, self._context, run):
            runner.run(data.body)

    def _should_run(self, condition, variables):
        if not condition:
            return True
        try:
            return evaluate_expression(condition, variables.current,
                                       resolve_variables=True)
        except Exception:
            msg = get_error_message()
            raise DataError(f'Invalid WHILE loop condition: {msg}')


class IfRunner:
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

    def _run_if_branch(self, branch, recursive_dry_run=False, syntax_error=None):
        context = self._context
        result = IfBranchResult(branch.type, branch.condition, starttime=get_timestamp())
        error = None
        if syntax_error:
            run_branch = False
            error = DataError(syntax_error, syntax=True)
        else:
            try:
                run_branch = self._should_run_branch(branch, context, recursive_dry_run)
            except DataError as err:
                error = err
                run_branch = False
        with StatusReporter(branch, result, context, run_branch):
            runner = BodyRunner(context, run_branch, self._templated)
            if not recursive_dry_run:
                runner.run(branch.body)
            if error and self._run:
                raise error
        return run_branch

    def _should_run_branch(self, branch, context, recursive_dry_run=False):
        condition = branch.condition
        variables = context.variables
        if context.dry_run:
            return not recursive_dry_run
        if not self._run:
            return False
        if condition is None:
            return True
        try:
            return evaluate_expression(condition, variables.current,
                                       resolve_variables=True)
        except Exception:
            msg = get_error_message()
            raise DataError(f'Invalid {branch.type} condition: {msg}')


class TryRunner:

    def __init__(self, context, run=True, templated=False):
        self._context = context
        self._run = run
        self._templated = templated

    def run(self, data):
        run = self._run
        with StatusReporter(data, TryResult(), self._context, run):
            if data.error:
                self._run_invalid(data)
                return
            error = self._run_try(data, run)
            run_excepts_or_else = self._should_run_excepts_or_else(error, run)
            if error:
                error = self._run_excepts(data, error, run=run_excepts_or_else)
                self._run_else(data, run=False)
            else:
                self._run_excepts(data, error, run=False)
                error = self._run_else(data, run=run_excepts_or_else)
            error = self._run_finally(data, run) or error
            if error:
                raise error

    def _run_invalid(self, data):
        error_reported = False
        for branch in data.body:
            result = TryBranchResult(branch.type, branch.patterns, branch.pattern_type,
                                     branch.variable)
            with StatusReporter(branch, result, self._context, run=False, suppress=True):
                runner = BodyRunner(self._context, run=False, templated=self._templated)
                runner.run(branch.body)
                if not error_reported:
                    error_reported = True
                    raise DataError(data.error, syntax=True)
        raise ExecutionFailed(data.error, syntax=True)

    def _run_try(self, data, run):
        result = TryBranchResult(data.TRY)
        return self._run_branch(data.try_branch, result, run)

    def _should_run_excepts_or_else(self, error, run):
        if not run:
            return False
        if not error:
            return True
        return not (error.skip or error.syntax or isinstance(error, ExecutionPassed))

    def _run_branch(self, branch, result, run=True, error=None):
        try:
            with StatusReporter(branch, result, self._context, run):
                if error:
                    raise error
                runner = BodyRunner(self._context, run, self._templated)
                runner.run(branch.body)
        except ExecutionStatus as err:
            return err
        else:
            return None

    def _run_excepts(self, data, error, run):
        for branch in data.except_branches:
            try:
                run_branch = run and self._should_run_except(branch, error)
            except DataError as err:
                run_branch = True
                pattern_error = err
            else:
                pattern_error = None
            result = TryBranchResult(branch.type, branch.patterns,
                                     branch.pattern_type, branch.variable)
            if run_branch:
                if branch.variable:
                    self._context.variables[branch.variable] = str(error)
                error = self._run_branch(branch, result, error=pattern_error)
                run = False
            else:
                self._run_branch(branch, result, run=False)
        return error

    def _should_run_except(self, branch, error):
        if not branch.patterns:
            return True
        matchers = {
            'GLOB': lambda m, p: Matcher(p, spaceless=False, caseless=False).match(m),
            'LITERAL': lambda m, p: m == p,
            'REGEXP': lambda m, p: re.match(rf'{p}\Z', m) is not None,
            'START': lambda m, p: m.startswith(p)
        }
        if branch.pattern_type:
            pattern_type = self._context.variables.replace_string(branch.pattern_type)
        else:
            pattern_type = 'LITERAL'
        matcher = matchers.get(pattern_type.upper())
        if not matcher:
            raise DataError(f"Invalid EXCEPT pattern type '{pattern_type}', "
                            f"expected {seq2str(matchers, lastsep=' or ')}.")
        for pattern in branch.patterns:
            if matcher(error.message, self._context.variables.replace_string(pattern)):
                return True
        return False

    def _run_else(self, data, run):
        if data.else_branch:
            result = TryBranchResult(data.ELSE)
            return self._run_branch(data.else_branch, result, run)

    def _run_finally(self, data, run):
        if data.finally_branch:
            result = TryBranchResult(data.FINALLY)
            try:
                with StatusReporter(data.finally_branch, result, self._context, run):
                    runner = BodyRunner(self._context, run, self._templated)
                    runner.run(data.finally_branch.body)
            except ExecutionStatus as err:
                return err
            else:
                return None


class WhileLimit:

    def __init__(self, on_limit=None, on_limit_message=None):
        self.on_limit = on_limit
        self.on_limit_message = on_limit_message

    @classmethod
    def create(cls, limit, on_limit, on_limit_message, variables):
        if on_limit_message:
            try:
                on_limit_message = variables.replace_string(on_limit_message)
            except DataError as err:
                raise DataError(f"Invalid WHILE loop 'on_limit_message': '{err}")
        on_limit = cls.parse_on_limit(variables, on_limit)
        if not limit:
            return IterationCountLimit(DEFAULT_WHILE_LIMIT,
                                       on_limit, on_limit_message)
        value = variables.replace_string(limit)
        if value.upper() == 'NONE':
            return NoLimit()
        try:
            count = int(value.replace(' ', ''))
        except ValueError:
            pass
        else:
            if count <= 0:
                raise DataError(f"Invalid WHILE loop limit: Iteration count must be "
                                f"a positive integer, got '{count}'.")
            return IterationCountLimit(count, on_limit, on_limit_message)
        try:
            secs = timestr_to_secs(value)
        except ValueError as err:
            raise DataError(f'Invalid WHILE loop limit: {err.args[0]}')
        else:
            return DurationLimit(secs, on_limit, on_limit_message)

    @classmethod
    def parse_on_limit(cls, variables, on_limit):
        if on_limit is None:
            return None
        try:
            on_limit = variables.replace_string(on_limit)
            if on_limit.upper() not in ['PASS', 'FAIL']:
                raise DataError("Value must be 'PASS' or 'FAIL'.")
        except DataError as err:
            raise DataError(f"Invalid WHILE loop 'on_limit' value '{on_limit}': {err}")
        else:
            return on_limit.lower()

    def limit_exceeded(self):
        on_limit_pass = self.on_limit == 'pass'
        if self.on_limit_message:
            raise LimitExceeded(on_limit_pass, self.on_limit_message)
        else:
            raise LimitExceeded(
                on_limit_pass,
                f"WHILE loop was aborted because it did not finish within the limit of {self}. "
                f"Use the 'limit' argument to increase or remove the limit if needed."
            )

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None


class DurationLimit(WhileLimit):

    def __init__(self, max_time, on_limit, on_limit_message):
        super().__init__(on_limit, on_limit_message)
        self.max_time = max_time
        self.start_time = None

    def __enter__(self):
        if not self.start_time:
            self.start_time = time.time()
        if time.time() - self.start_time > self.max_time:
            self.limit_exceeded()

    def __str__(self):
        return secs_to_timestr(self.max_time)


class IterationCountLimit(WhileLimit):

    def __init__(self, max_iterations, on_limit, on_limit_message):
        super().__init__(on_limit, on_limit_message)
        self.max_iterations = max_iterations
        self.current_iterations = 0

    def __enter__(self):
        if self.current_iterations >= self.max_iterations:
            self.limit_exceeded()
        self.current_iterations += 1

    def __str__(self):
        return f'{self.max_iterations} iterations'


class NoLimit(WhileLimit):

    def __enter__(self):
        pass


class LimitExceeded(ExecutionFailed):

    def __init__(self, on_limit_pass, message):
        super().__init__(message)
        self.on_limit_pass = on_limit_pass
