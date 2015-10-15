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

from robot.errors import ExecutionFailed, PassExecution
from robot.utils import py2to3, unic


@py2to3
class Failure(object):

    def __init__(self):
        self.setup = None
        self.test = None
        self.teardown = None

    def __nonzero__(self):
        return bool(self.setup or self.test or self.teardown)


@py2to3
class Exit(object):

    def __init__(self, failure_mode=False, error_mode=False,
                 skip_teardown_mode=False):
        self.failure_mode = failure_mode
        self.error_mode = error_mode
        self.skip_teardown_mode = skip_teardown_mode
        self.failure = False
        self.error = False
        self.fatal = False

    def failure_occurred(self, failure=None, critical=False):
        if isinstance(failure, ExecutionFailed) and failure.exit:
            self.fatal = True
        if critical and self.failure_mode:
            self.failure = True

    def error_occurred(self):
        if self.error_mode:
            self.error = True

    @property
    def teardown_allowed(self):
        return not (self.skip_teardown_mode and self)

    def __nonzero__(self):
        return self.failure or self.error or self.fatal


class _ExecutionStatus(object):

    def __init__(self, parent=None, *exit_modes):
        self.parent = parent
        self.children = []
        self.failure = Failure()
        self.exit = parent.exit if parent else Exit(*exit_modes)
        self._teardown_allowed = False
        if parent:
            parent.children.append(self)

    def setup_executed(self, failure=None):
        if failure and not isinstance(failure, PassExecution):
            self.failure.setup = unic(failure)
            self.exit.failure_occurred(failure)
        self._teardown_allowed = True

    def teardown_executed(self, failure=None):
        if failure and not isinstance(failure, PassExecution):
            self.failure.teardown = unic(failure)
            self.exit.failure_occurred(failure)

    def critical_failure_occurred(self):
        self.exit.failure_occurred(critical=True)

    def error_occurred(self):
        self.exit.error_occurred()

    @property
    def teardown_allowed(self):
        return self.exit.teardown_allowed and self._teardown_allowed

    @property
    def failures(self):
        return bool(self.parent and self.parent.failures or
                    self.failure or self.exit)

    def _parent_failures(self):
        return self.parent and self.parent.failures

    @property
    def status(self):
        return 'FAIL' if self.failures else 'PASS'

    @property
    def message(self):
        if self.failure or self.exit:
            return self._my_message()
        if self.parent and self.parent.failures:
            return self._parent_message()
        return ''

    def _my_message(self):
        raise NotImplementedError

    def _parent_message(self):
        return ParentMessage(self.parent).message


class SuiteStatus(_ExecutionStatus):

    def __init__(self, parent=None, exit_on_failure_mode=False,
                 exit_on_error_mode=False,
                 skip_teardown_on_exit_mode=False):
        _ExecutionStatus.__init__(self, parent, exit_on_failure_mode,
                                  exit_on_error_mode,
                                  skip_teardown_on_exit_mode)

    def _my_message(self):
        return SuiteMessage(self).message


class TestStatus(_ExecutionStatus):

    def __init__(self, parent, critical):
        _ExecutionStatus.__init__(self, parent)
        self.exit = parent.exit
        self._critical = critical

    def test_failed(self, failure):
        self.failure.test = unic(failure)
        self.exit.failure_occurred(failure, self._critical)

    def _my_message(self):
        return TestMessage(self).message


class _Message(object):
    setup_message = NotImplemented
    teardown_message = NotImplemented
    also_teardown_message = NotImplemented

    def __init__(self, status):
        self.failure = status.failure

    @property
    def message(self):
        msg = self._get_message_before_teardown()
        return self._get_message_after_teardown(msg)

    def _get_message_before_teardown(self):
        if self.failure.setup:
            return self.setup_message % self.failure.setup
        return self.failure.test or ''

    def _get_message_after_teardown(self, msg):
        if not self.failure.teardown:
            return msg
        if not msg:
            return self.teardown_message % self.failure.teardown
        return self.also_teardown_message % (msg, self.failure.teardown)


class TestMessage(_Message):
    setup_message = 'Setup failed:\n%s'
    teardown_message = 'Teardown failed:\n%s'
    also_teardown_message = '%s\n\nAlso teardown failed:\n%s'
    exit_on_fatal_message = 'Test execution stopped due to a fatal error.'
    exit_on_failure_message = \
        'Critical failure occurred and exit-on-failure mode is in use.'
    exit_on_error_message = 'Error occurred and exit-on-error mode is in use.'

    def __init__(self, status):
        _Message.__init__(self, status)
        self.exit = status.exit

    @property
    def message(self):
        message = super(TestMessage, self).message
        if message:
            return message
        if self.exit.failure:
            return self.exit_on_failure_message
        if self.exit.fatal:
            return self.exit_on_fatal_message
        if self.exit.error:
            return self.exit_on_error_message
        return ''


class SuiteMessage(_Message):
    setup_message = 'Suite setup failed:\n%s'
    teardown_message = 'Suite teardown failed:\n%s'
    also_teardown_message = '%s\n\nAlso suite teardown failed:\n%s'


class ParentMessage(SuiteMessage):
    setup_message = 'Parent suite setup failed:\n%s'
    teardown_message = 'Parent suite teardown failed:\n%s'
    also_teardown_message = '%s\n\nAlso parent suite teardown failed:\n%s'

    def __init__(self, status):
        while status.parent and status.parent.failures:
            status = status.parent
        SuiteMessage.__init__(self, status)
