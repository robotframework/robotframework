#  Copyright 2008-2014 Nokia Solutions and Networks
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

from robot.errors import PassExecution


class _ExecutionStatus(object):

    def __init__(self, parent=None):
        self.parent = parent
        self.setup_failure = None
        self.test_failure = None
        self.teardown_failure = None
        self._teardown_allowed = False
        self.exiting_on_failure = parent.exiting_on_failure if parent else False
        self.exiting_on_fatal = parent.exiting_on_fatal if parent else False
        self.skip_teardown_on_exit_mode = parent.skip_teardown_on_exit_mode if parent else False

    def setup_executed(self, failure=None):
        if failure and not isinstance(failure, PassExecution):
            self.setup_failure = unicode(failure)
            self._handle_possible_fatal(failure)
        self._teardown_allowed = True

    def teardown_executed(self, failure=None):
        if failure and not isinstance(failure, PassExecution):
            self.teardown_failure = unicode(failure)
            self._handle_possible_fatal(failure)

    @property
    def teardown_allowed(self):
        if self.skip_teardown_on_exit_mode and (self.exiting_on_failure or
                                                self.exiting_on_fatal):
            return False
        return self._teardown_allowed

    @property
    def failures(self):
        return bool(self._parent_failures() or self._my_failures())

    def _parent_failures(self):
        return self.parent and self.parent.failures

    def _my_failures(self):
        return bool(self.setup_failure or
                    self.teardown_failure or
                    self.test_failure or
                    self.exiting_on_failure or
                    self.exiting_on_fatal)

    @property
    def status(self):
        return 'FAIL' if self.failures else 'PASS'

    @property
    def message(self):
        if self._my_failures():
            return self._my_message()
        if self._parent_failures():
            return self._parent_message()
        return ''

    def _my_message(self):
        raise NotImplementedError

    def _parent_message(self):
        return ParentMessage(self.parent).message

    def _handle_possible_fatal(self, failure):
        if getattr(failure, 'exit', False):
            if self.parent:
                self.parent.fatal_failure()
            self.exiting_on_fatal = True


class SuiteStatus(_ExecutionStatus):

    def __init__(self, parent, exit_on_failure_mode=False,
                 skip_teardown_on_exit_mode=False):
        _ExecutionStatus.__init__(self, parent)
        self.exit_on_failure_mode = exit_on_failure_mode
        self.skip_teardown_on_exit_mode = skip_teardown_on_exit_mode

    def critical_failure(self):
        if self.exit_on_failure_mode:
            self.exiting_on_failure = True
        if self.parent:
            self.parent.critical_failure()

    def fatal_failure(self):
        self.exiting_on_fatal = True
        if self.parent:
            self.parent.fatal_failure()

    def _my_message(self):
        return SuiteMessage(self).message


class TestStatus(_ExecutionStatus):

    def __init__(self, suite_status):
        _ExecutionStatus.__init__(self, suite_status)

    def test_failed(self, failure, critical):
        self.test_failure = unicode(failure)
        if critical:
            self.parent.critical_failure()
            self.exiting_on_failure = self.parent.exit_on_failure_mode
        self._handle_possible_fatal(failure)

    def _my_message(self):
        return TestMessage(self).message


class _Message(object):
    setup_message = NotImplemented
    teardown_message = NotImplemented
    also_teardown_message = NotImplemented

    def __init__(self, status):
        self.setup_failure = status.setup_failure
        self.test_failure = status.test_failure or ''
        self.teardown_failure = status.teardown_failure

    @property
    def message(self):
        msg = self._get_message_before_teardown()
        return self._get_message_after_teardown(msg)

    def _get_message_before_teardown(self):
        if self.setup_failure:
            return self.setup_message % self.setup_failure
        return self.test_failure

    def _get_message_after_teardown(self, msg):
        if not self.teardown_failure:
            return msg
        if not msg:
            return self.teardown_message % self.teardown_failure
        return self.also_teardown_message % (msg, self.teardown_failure)


class TestMessage(_Message):
    setup_message = 'Setup failed:\n%s'
    teardown_message = 'Teardown failed:\n%s'
    also_teardown_message = '%s\n\nAlso teardown failed:\n%s'
    exit_on_fatal_message = 'Test execution stopped due to a fatal error.'
    exit_on_failure_message = \
        'Critical failure occurred and exit-on-failure mode is in use.'

    def __init__(self, status):
        _Message.__init__(self, status)
        self.exiting_on_failure = status.exiting_on_failure
        self.exiting_on_fatal = status.exiting_on_fatal

    @property
    def message(self):
        message = super(TestMessage, self).message
        if message:
            return message
        if self.exiting_on_failure:
            return self.exit_on_failure_message
        if self.exiting_on_fatal:
            return self.exit_on_fatal_message
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
