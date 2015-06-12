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

from robot.errors import (ExecutionFailed, ExecutionFailures, ExecutionPassed,
                          ExitForLoop, ContinueForLoop, DataError,
                          HandlerExecutionFailed)
from robot.result.keyword import Keyword as KeywordResult
from robot.utils import (format_assign_message, frange, get_error_message,
                         get_timestamp, plural_or_not as s, type_name,
                         is_list_like)
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
            runner = ForLoopRunner(self._context, self._templated, kw.flavor)
        else:
            runner = NormalRunner(self._context)
        return runner.run(kw, name=name)


class NormalRunner(object):

    def __init__(self, context):
        self._context = context

    def run(self, kw, name=None):
        handler = self._context.get_handler(name or kw.name)
        handler.init_keyword(self._context.variables)
        assigner = VariableAssigner(kw.assign)
        result = KeywordResult(kwname=handler.name or '',
                               libname=handler.libname or '',
                               doc=handler.shortdoc,
                               args=kw.args,
                               assign=assigner.assignment,
                               tags=handler.tags,
                               timeout=getattr(handler, 'timeout', ''),
                               type=kw.type)
        dry_run_lib_kw = self._context.dry_run and handler.type == 'library'
        with StatusReporter(self._context, result, dry_run_lib_kw):
            self._warn_if_deprecated(result.name, result.doc)
            return self._run_and_assign(handler, kw.args, assigner)

    def _warn_if_deprecated(self, name, doc):
        if doc.startswith('*DEPRECATED') and '*' in doc[1:]:
            message = ' ' + doc.split('*', 2)[-1].strip()
            self._context.warn("Keyword '%s' is deprecated.%s" % (name, message))

    def _run_and_assign(self, handler, args, assigner):
        syntax_error_reporter = SyntaxErrorReporter(self._context)
        with syntax_error_reporter:
            assigner.validate_assignment()
        return_value, exception = self._run(handler, args)
        if not exception or exception.can_continue(self._context.in_teardown):
            with syntax_error_reporter:
                assigner.assign(self._context, return_value)
        if exception:
            raise exception
        return return_value

    def _run(self, handler, args):
        return_value = exception = None
        try:
            return_value = handler.run(self._context, args)
        except ExecutionFailed as err:
            exception = err
        except:
            exception = self._get_and_report_failure()
        if exception:
            return_value = exception.return_value
        return return_value, exception

    def _get_and_report_failure(self):
        failure = HandlerExecutionFailed()
        if failure.timeout:
            self._context.timeout_occurred = True
        self._context.fail(failure.full_message)
        if failure.traceback:
            self._context.debug(failure.traceback)
        return failure


class BasicForLoopRunner(object):
    """A basic For Loop.

    To make a new kind of For loop, subclass this and override
    _flavor_name() and _transform_items(items).
    """

    def __init__(self, context, templated=False):
        self._context = context
        self._templated = templated

    def run(self, data, name=None):
        result = KeywordResult(kwname=self._get_name(data),
                               type=data.FOR_LOOP_TYPE)
        with StatusReporter(self._context, result):
            with SyntaxErrorReporter(self._context):
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
            var_count = len(data.variables)
            for i in range(0, self._original_values_per_iteration(values), var_count):
                yield values[i:i+var_count]
        else:
            yield data.variables

    def _replace_variables(self, data):
        values = self._context.variables.replace_list(data.values)
        values = self._transform_items(values)
        if self._original_values_per_iteration(values) % len(data.variables) == 0:
            return values
        raise DataError('Number of FOR loop values should be multiple of '
                        'variables. Got %d variables but %d value%s.'
                        % (len(data.variables), len(values), s(values)))

    def _run_one_round(self, data, values):
        name = ', '.join(format_assign_message(var, item)
                         for var, item in zip(data.variables, values))
        result = KeywordResult(kwname=name,
                               type=data.FOR_ITEM_TYPE)
        for var, value in zip(data.variables, values):
            self._context.variables[var] = value
        runner = KeywordRunner(self._context, self._templated)
        with StatusReporter(self._context, result):
            runner.run_keywords(data.keywords)

    def _transform_items(self, items):
        return items

    def _original_values_per_iteration(self, values):
        """
        The number of values per iteration;
        used to check if we have (a multiple of this) values.

        This is its own method to support loops like ForInEnumerate
        which add/remove items to the pool.
        """
        return len(values)


class ForInRangeLoopRunner(BasicForLoopRunner):
    def __init__(self, context, templated=False):
        super(ForInRangeLoopRunner, self).__init__(context, templated)

    def _flavor_name(self):
        return 'IN RANGE'

    def _transform_items(self, items):
        return self._get_range_items(items)

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
        number = eval(str(item), {})
        if not isinstance(number, (int, long, float)):
            raise TypeError("Expected number, got %s." % type_name(item))
        return number


class ForInZipLoopRunner(BasicForLoopRunner):
    def __init__(self, context, templated=False):
        super(ForInZipLoopRunner, self).__init__(context, templated)

    def _flavor_name(self):
        return 'IN ZIP'

    def _replace_variables(self, data):
        """
        Make sure we have as many loop-variables as zipped-iterables.

        (Other than that, delegate to the superclass.)
        """
        values = super(ForInZipLoopRunner, self)._replace_variables(data)
        if len(data.variables) == len(data.values):
            return values
        raise DataError("Expected %d Loop variables, but found %d"
                % (len(data.values), len(data.variables)))

    def _transform_items(self, items):
        answer = list()
        for item in items:
            if not is_list_like(item):
                # Checking here because _validate() doesn't have access
                # to the actual values.
                raise DataError("For-In-Zip Loop items must all be List-like (but not Strings); got %s with value '%s'" % (item.__class__, item))
        for zipped_item in zip(*items):
            answer.extend(zipped_item)
        return answer


class ForInEnumerateLoopRunner(BasicForLoopRunner):
    def __init__(self, context, templated=False):
        super(ForInEnumerateLoopRunner, self).__init__(context, templated)

    def _flavor_name(self):
        return 'IN ENUMERATE'

    def _transform_items(self, items):
        answer = list()
        for zipped_item in zip(*items):
            answer.extend(zipped_item)
        return answer

    @property
    def _original_values_per_iteration(self, values):
        """
        The number of values per iteration;
        used to check if we have (a multiple of this) values.

        This is its own method to support loops like ForInEnumerate
        which add/remove items to the pool.
        """
        if len(values) < 2:
            raise DataError('FOR IN ENUMERATE expected 2 or more loop variables, got %d.'
                    % len(values))
        return len(values) - 1

    def _get_values_for_one_round(self, data):
        for idx, values in enumerate(super(ForInEnumerateLoopRunner, self)
                ._get_values_for_one_round(data)):
            yield (idx,) + values


# Defining this dict here in for potentially easier extension by libraries...
# ...unless that's a terrible idea?
def ForLoopRunner(context, templated=False, flavor='IN'):
    FOR_LOOP_FLAVORS = dict(
            IN=BasicForLoopRunner,
            INRANGE=ForInRangeLoopRunner,
            INZIP=ForInZipLoopRunner,
            INENUMERATE=ForInEnumerateLoopRunner,
            )
    flavor_key = flavor.upper().replace(' ', '')
    if flavor_key in FOR_LOOP_FLAVORS:
        runner_class = FOR_LOOP_FLAVORS[flavor_key]
        return runner_class(context, templated)
    else:
        return InvalidForLoopRunner(context, flavor_key, flavor, FOR_LOOP_FLAVORS.keys())


class InvalidForLoopRunner(BasicForLoopRunner):
    """
    Used to send an error from ForLoopRunner() if it sees an unexpected error.

    We can't simply throw a DataError from ForLoopRunner() because that happens
    outside the "with StatusReporter(...)" blocks.

    """
    def __init__(self, context, flavor, pretty_flavor, expected):
        super(InvalidForLoopRunner, self).__init__(context, False)
        self.flavor = flavor
        self.pretty_flavor = pretty_flavor
        self.expected = repr(sorted(expected))

    def _run(self, data, *args, **kwargs):
        raise DataError(
            "Unexpected For-loop type %s (%s); expected one of %s (but with spaces)" %
            (self.flavor, self.pretty_flavor, self.expected))


class StatusReporter(object):

    def __init__(self, context, result, dry_run_lib_kw=False):
        self._context = context
        self._result = result
        self._pass_status = 'PASS' if not dry_run_lib_kw else 'NOT_RUN'

    def __enter__(self):
        self._result.starttime = get_timestamp()
        self._context.start_keyword(self._result)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            self._result.status = self._pass_status
        elif isinstance(exc_val, ExecutionFailed):
            self._result.status = exc_val.status
            if self._result.type == self._result.TEARDOWN_TYPE:
                self._result.message = unicode(exc_val)
        self._result.endtime = get_timestamp()
        self._context.end_keyword(self._result)


class SyntaxErrorReporter(object):

    def __init__(self, context):
        self._context = context

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, DataError):
            msg = unicode(exc_val)
            self._context.fail(msg)
            raise ExecutionFailed(msg, syntax=True)
