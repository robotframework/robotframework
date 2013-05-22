#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

import utils


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
        return self.__unicode__()

    def __unicode__(self):
        # Needed to handle exceptions w/ Unicode correctly on Python 2.5
        return unicode(self.args[0]) if self.args else u''


class FrameworkError(RobotError):
    """Can be used when the core framework goes to unexpected state.

    It is good to explicitly raise a FrameworkError if some framework
    component is used incorrectly. This is pretty much same as
    'Internal Error' and should of course never happen.
    """


class DataError(RobotError):
    """Used when the provided test data is invalid.

    DataErrors are not be caught by keywords that run other keywords
    (e.g. `Run Keyword And Expect Error`). Libraries should thus use
    this exception with care.
    """


class UnrecognizedParameterError(RobotError):
    """Used when non allowed parameters are given for a keyword."""



class TimeoutError(RobotError):
    """Used when a test or keyword timeout occurs.

    This exception is handled specially so that execution of the
    current test is always stopped immediately and it is not caught by
    keywords executing other keywords (e.g. `Run Keyword And Expect
    Error`). Libraries should thus NOT use this exception themselves.
    """


class Information(RobotError):
    """Used by argument parser with --help or --version."""


class ExecutionFailed(RobotError):
    """Used for communicating failures in test execution."""

    def __init__(self, message, timeout=False, syntax=False, exit=False,
                 continue_on_failure=False, return_value=None):
        if '\r\n' in message:
            message = message.replace('\r\n', '\n')
        RobotError.__init__(self, utils.cut_long_message(message))
        self.timeout = timeout
        self.syntax = syntax
        self.exit = exit
        self.continue_on_failure = continue_on_failure
        self.return_value = return_value

    @property
    def dont_continue(self):
        return self.timeout or self.syntax or self.exit

    def _get_continue_on_failure(self):
        return self._continue_on_failure

    def _set_continue_on_failure(self, continue_on_failure):
        self._continue_on_failure = continue_on_failure
        for child in getattr(self, '_errors', []):
            child.continue_on_failure = continue_on_failure

    continue_on_failure = property(_get_continue_on_failure,
                                   _set_continue_on_failure)

    def can_continue(self, teardown=False, templated=False, dry_run=False):
        if dry_run:
            return True
        if self.dont_continue and not (teardown and self.syntax):
            return False
        if teardown or templated:
            return True
        return self.continue_on_failure

    def get_errors(self):
        return [self]


class HandlerExecutionFailed(ExecutionFailed):

    def __init__(self):
        details = utils.ErrorDetails()
        timeout = isinstance(details.error, TimeoutError)
        syntax = isinstance(details.error, DataError)
        exit = self._get(details.error, 'EXIT_ON_FAILURE')
        continue_on_failure = self._get(details.error, 'CONTINUE_ON_FAILURE')

        if self._get(details.error, 'EXIT_FOR_LOOP'):
            from robot.output import LOGGER
            LOGGER.warn('Using ROBOT_EXIT_FOR_LOOP is deprecated in 2.8.')
            raise ExitForLoop

        ExecutionFailed.__init__(self, details.message, timeout, syntax,
                                 exit, continue_on_failure)

        self.full_message = details.message
        self.traceback = details.traceback

    def _get(self, error, attr):
        return bool(getattr(error, 'ROBOT_' + attr, False))


class ExecutionFailures(ExecutionFailed):

    def __init__(self, errors, message=None):
        message = message or self._format_message([unicode(e) for e in errors])
        ExecutionFailed.__init__(self, message, **self._get_attrs(errors))
        self._errors = errors

    def _format_message(self, messages):
        if len(messages) == 1:
            return messages[0]
        lines = ['Several failures occurred:'] \
                + ['%d) %s' % (i+1, m) for i, m in enumerate(messages)]
        return '\n\n'.join(lines)

    def _get_attrs(self, errors):
        return {'timeout': any(err.timeout for err in errors),
                'syntax': any(err.syntax for err in errors),
                'exit': any(err.exit for err in errors),
                'continue_on_failure': all(err.continue_on_failure for err in errors)
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
        run_msg = unicode(run_errors or '')
        td_msg = unicode(teardown_errors or '')
        if not td_msg:
            return run_msg
        if not run_msg:
            return 'Keyword teardown failed:\n%s' % td_msg
        return '%s\n\nAlso keyword teardown failed:\n%s' % (run_msg, td_msg)


class _ExecutionPassed(ExecutionFailed):

    def __init__(self, message, *args, **kwargs):
        ExecutionFailed.__init__(self,
                                 message if message else 'Execution Passed called',
                                 *args, **kwargs)
        self._earlier_failures = []

    def set_earlier_failures(self, failures):
        if failures:
            self._earlier_failures.extend(failures)

    @property
    def earlier_failures(self):
        if not self._earlier_failures:
            return None
        return ExecutionFailures(self._earlier_failures)


class ContinueForLoop(_ExecutionPassed):

    def __init__(self):
        _ExecutionPassed.__init__(self,
                                  'Continue for loop without enclosing for loop.')


class ExecutionPassed(_ExecutionPassed):
    pass


class ExitForLoop(_ExecutionPassed):

    def __init__(self):
        _ExecutionPassed.__init__(self,
                                  'Exit for loop without enclosing for loop.')


class ReturnFromKeyword(_ExecutionPassed):

    def __init__(self, return_value):
        _ExecutionPassed.__init__(self,
                                 'Return from keyword without enclosing keyword',
                                 return_value=return_value)


class RemoteError(RobotError):
    """Used by Remote library to report remote errors."""
