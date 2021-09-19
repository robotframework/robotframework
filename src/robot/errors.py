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

"""Exceptions and return codes used internally.

External libraries should not used exceptions defined here.
"""

try:
    unicode
except NameError:
    unicode = str


# Return codes from Robot and Rebot.
# RC below 250 is the number of failed critical tests and exactly 250
# means that number or more such failures.
INFO_PRINTED    = 251   # --help or --version
DATA_ERROR      = 252   # Invalid data or cli args
STOPPED_BY_USER = 253   # KeyboardInterrupt or SystemExit
FRAMEWORK_ERROR = 255   # Unexpected error


class RobotError(Exception):
    """Base class for Robot Framework errors.

    Do not raise this method but use more specific errors instead.
    """

    def __init__(self, message='', details=''):
        Exception.__init__(self, message)
        self.details = details

    @property
    def message(self):
        return unicode(self)


class FrameworkError(RobotError):
    """Can be used when the core framework goes to unexpected state.

    It is good to explicitly raise a FrameworkError if some framework
    component is used incorrectly. This is pretty much same as
    'Internal Error' and should of course never happen.
    """


class DataError(RobotError):
    """Used when the provided test data is invalid.

    DataErrors are not caught by keywords that run other keywords
    (e.g. `Run Keyword And Expect Error`).
    """


class VariableError(DataError):
    """Used when variable does not exist.

    VariableErrors are caught by keywords that run other keywords
    (e.g. `Run Keyword And Expect Error`).
    """


class KeywordError(DataError):
    """Used when no keyword is found or there is more than one match.

    KeywordErrors are caught by keywords that run other keywords
    (e.g. `Run Keyword And Expect Error`).
    """


class TimeoutError(RobotError):
    """Used when a test or keyword timeout occurs.

    This exception is handled specially so that execution of the
    current test is always stopped immediately and it is not caught by
    keywords executing other keywords (e.g. `Run Keyword And Expect Error`).
    """

    def __init__(self, message='', test_timeout=True):
        RobotError.__init__(self, message)
        self.test_timeout = test_timeout

    @property
    def keyword_timeout(self):
        return not self.test_timeout


class Information(RobotError):
    """Used by argument parser with --help or --version."""


class ExecutionStatus(RobotError):
    """Base class for exceptions communicating status in test execution."""

    def __init__(self, message, test_timeout=False, keyword_timeout=False,
                 syntax=False, exit=False, continue_on_failure=False,
                 skip=False, return_value=None):
        if '\r\n' in message:
            message = message.replace('\r\n', '\n')
        from robot.utils import cut_long_message
        RobotError.__init__(self, cut_long_message(message))
        self.test_timeout = test_timeout
        self.keyword_timeout = keyword_timeout
        self.syntax = syntax
        self.exit = exit
        self._continue_on_failure = continue_on_failure
        self.skip = skip
        self.return_value = return_value

    @property
    def timeout(self):
        return self.test_timeout or self.keyword_timeout

    @property
    def dont_continue(self):
        return self.timeout or self.syntax or self.exit

    @property
    def continue_on_failure(self):
        return self._continue_on_failure

    @continue_on_failure.setter
    def continue_on_failure(self, continue_on_failure):
        self._continue_on_failure = continue_on_failure
        for child in getattr(self, '_errors', []):
            if child is not self:
                child.continue_on_failure = continue_on_failure

    def can_continue(self, context, templated=False):
        if context.dry_run:
            return True
        if self.syntax or self.exit or self.skip or self.test_timeout:
            return False
        if templated:
            return True
        if self.keyword_timeout:
            if context.in_teardown:
                self.keyword_timeout = False
            return False
        if context.in_teardown or context.continue_on_failure:
            return True
        return self.continue_on_failure

    def get_errors(self):
        return [self]

    @property
    def status(self):
        return 'FAIL' if not self.skip else 'SKIP'


class ExecutionFailed(ExecutionStatus):
    """Used for communicating failures in test execution."""


class HandlerExecutionFailed(ExecutionFailed):

    def __init__(self, details):
        error = details.error
        timeout = isinstance(error, TimeoutError)
        test_timeout = timeout and error.test_timeout
        keyword_timeout = timeout and error.keyword_timeout
        syntax = (isinstance(error, DataError)
                  and not isinstance(error, (KeywordError, VariableError)))
        exit_on_failure = self._get(error, 'EXIT_ON_FAILURE')
        continue_on_failure = self._get(error, 'CONTINUE_ON_FAILURE')
        skip = self._get(error, 'SKIP_EXECUTION')
        ExecutionFailed.__init__(self, details.message, test_timeout,
                                 keyword_timeout, syntax, exit_on_failure,
                                 continue_on_failure, skip)
        self.full_message = details.message
        self.traceback = details.traceback

    def _get(self, error, attr):
        return bool(getattr(error, 'ROBOT_' + attr, False))


class ExecutionFailures(ExecutionFailed):

    def __init__(self, errors, message=None):
        message = message or self._format_message(errors)
        ExecutionFailed.__init__(self, message, **self._get_attrs(errors))
        self._errors = errors

    def _format_message(self, errors):
        messages = [e.message for e in errors]
        if len(messages) == 1:
            return messages[0]
        prefix = 'Several failures occurred:'
        if any(msg.startswith('*HTML*') for msg in messages):
            html_prefix = '*HTML* '
            messages = [self._html_format(msg) for msg in messages]
        else:
            html_prefix = ''
        if any(e.skip for e in errors):
            skip_idx = errors.index([e for e in errors if e.skip][0])
            skip_msg = messages[skip_idx]
            messages = messages[:skip_idx] + messages[skip_idx+1:]
            if len(messages) == 1:
                return '%s%s\n\nAlso failure occurred:\n%s' \
                       % (html_prefix, skip_msg, messages[0])
            prefix = '%s\n\nAlso failures occurred:' % skip_msg
        return '\n\n'.join(
            [html_prefix + prefix] +
            ['%d) %s' % (i, m) for i, m in enumerate(messages, start=1)]
        )

    def _html_format(self, msg):
        from robot.utils import html_escape
        if msg.startswith('*HTML*'):
            return msg[6:].lstrip()
        return html_escape(msg)

    def _get_attrs(self, errors):
        return {
            'test_timeout': any(e.test_timeout for e in errors),
            'keyword_timeout': any(e.keyword_timeout for e in errors),
            'syntax': any(e.syntax for e in errors),
            'exit': any(e.exit for e in errors),
            'continue_on_failure': all(e.continue_on_failure for e in errors),
            'skip': any(e.skip for e in errors)
        }

    def get_errors(self):
        return self._errors


class UserKeywordExecutionFailed(ExecutionFailures):

    def __init__(self, run_errors=None, teardown_errors=None):
        errors = self._get_active_errors(run_errors, teardown_errors)
        message = self._get_message(run_errors, teardown_errors)
        ExecutionFailures.__init__(self, errors, message)
        if run_errors and not teardown_errors:
            self._errors = run_errors.get_errors()
        else:
            self._errors = [self]

    def _get_active_errors(self, *errors):
        return [err for err in errors if err]

    def _get_message(self, run_errors, teardown_errors):
        run_msg = run_errors.message if run_errors else ''
        td_msg = teardown_errors.message if teardown_errors else ''
        if not td_msg:
            return run_msg
        if not run_msg:
            return 'Keyword teardown failed:\n%s' % td_msg
        return '%s\n\nAlso keyword teardown failed:\n%s' % (run_msg, td_msg)


class ExecutionPassed(ExecutionStatus):
    """Base class for all exceptions communicating that execution passed.

    Should not be raised directly, but more detailed exceptions used instead.
    """

    def __init__(self, message=None, **kwargs):
        ExecutionStatus.__init__(self, message or self._get_message(), **kwargs)
        self._earlier_failures = []

    def _get_message(self):
        from robot.utils import printable_name
        return ("Invalid '%s' usage."
                % printable_name(type(self).__name__, code_style=True))

    def set_earlier_failures(self, failures):
        if failures:
            self._earlier_failures = list(failures) + self._earlier_failures

    @property
    def earlier_failures(self):
        if not self._earlier_failures:
            return None
        return ExecutionFailures(self._earlier_failures)

    @property
    def status(self):
        return 'PASS' if not self._earlier_failures else 'FAIL'


class PassExecution(ExecutionPassed):
    """Used by 'Pass Execution' keyword."""

    def __init__(self, message):
        ExecutionPassed.__init__(self, message)


class ContinueForLoop(ExecutionPassed):
    """Used by 'Continue For Loop' keyword."""


class ExitForLoop(ExecutionPassed):
    """Used by 'Exit For Loop' keyword."""


class ReturnFromKeyword(ExecutionPassed):
    """Used by 'Return From Keyword' keyword."""

    def __init__(self, return_value=None, failures=None):
        ExecutionPassed.__init__(self, return_value=return_value)
        if failures:
            self.set_earlier_failures(failures)


class RemoteError(RobotError):
    """Used by Remote library to report remote errors."""

    def __init__(self, message='', details='', fatal=False, continuable=False):
        RobotError.__init__(self, message, details)
        self.ROBOT_EXIT_ON_FAILURE = fatal
        self.ROBOT_CONTINUE_ON_FAILURE = continuable
