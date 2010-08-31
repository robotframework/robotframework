#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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
    def __init__(self, message=''):
        Exception.__init__(self, message)

    def __unicode__(self):
        # Needed to handle exceptions w/ Unicode correctly on Python 2.5
        return unicode(self.args[0])


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
                 cont=False, exit_for_loop=False):
        RobotError.__init__(self, utils.cut_long_message(message))
        self.timeout = timeout
        self.syntax = syntax
        self.exit = exit
        self.cont = cont
        self.exit_for_loop = exit_for_loop

    @property
    def dont_cont(self):
        return self.timeout or self.syntax or self.exit

    # Python 2.6 property decorators would have nice `setter` attribute:
    # http://docs.python.org/library/functions.html#property
    cont = property(lambda self: self._cont and not self.dont_cont,
                    lambda self, cont: setattr(self, '_cont', cont))

    def can_continue(self, teardown=False, templated=False, dry_run=False):
        if dry_run:
            return True
        if self.dont_cont and not (teardown and self.syntax):
            return False
        if teardown or templated:
            return True
        return self.cont

    def get_errors(self):
        return [self]


class HandlerExecutionFailed(ExecutionFailed):

    def __init__(self):
        details = utils.ErrorDetails()
        timeout = isinstance(details.error, TimeoutError)
        syntax = isinstance(details.error, DataError)
        exit = bool(getattr(details.error, 'ROBOT_EXIT_ON_FAILURE', False))
        cont = bool(getattr(details.error, 'ROBOT_CONTINUE_ON_FAILURE', False))
        exit_for_loop = bool(getattr(details.error, 'ROBOT_EXIT_FOR_LOOP', False))
        ExecutionFailed.__init__(self, details.message, timeout, syntax,
                                 exit, cont, exit_for_loop)
        self.traceback = details.traceback


class ExecutionFailures(ExecutionFailed):

    def __init__(self, errors):
        ExecutionFailed.__init__(self, self._format_message(errors),
                                 any(err.timeout for err in errors),
                                 any(err.syntax for err in errors),
                                 any(err.exit for err in errors),
                                 all(err.cont for err in errors),
                                 all(err.exit_for_loop for err in errors))
        self._errors = errors

    def _format_message(self, errors):
        if len(errors) == 1:
            return unicode(errors[0])
        lines = ['Several failures occurred:'] \
                + ['%d) %s' % (i+1, unicode(e)) for i, e in enumerate(errors)]
        return '\n\n'.join(lines)

    def get_errors(self):
        return self._errors


class RemoteError(RobotError):
    """Used by Remote library to report remote errors."""

    def __init__(self, message, traceback):
        RobotError.__init__(self, message)
        self.traceback = traceback
