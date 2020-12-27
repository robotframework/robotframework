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

from robot.errors import ExecutionFailed, PassExecution, SkipExecution
from robot.model.tags import TagPatterns
from robot.utils import html_escape, py2to3, unic


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

    def failure_occurred(self, failure=None):
        if isinstance(failure, ExecutionFailed) and failure.exit:
            self.fatal = True
        if self.failure_mode:
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
        self.skipped = False
        self._teardown_allowed = False
        if parent:
            parent.children.append(self)

    def setup_executed(self, failure=None):
        if failure and not isinstance(failure, PassExecution):
            self.failure.setup = unic(failure)
            self.exit.failure_occurred(failure)
            self.skipped = isinstance(failure, SkipExecution)
        self._teardown_allowed = True

    def teardown_executed(self, failure=None):
        if failure and not isinstance(failure, PassExecution):
            self.failure.teardown = unic(failure)
            self.exit.failure_occurred(failure)

    def failure_occurred(self):
        self.exit.failure_occurred()

    def error_occurred(self):
        self.exit.error_occurred()

    @property
    def teardown_allowed(self):
        return self.exit.teardown_allowed and self._teardown_allowed

    @property
    def failures(self):
        return bool(self.parent and self.parent.failures or
                    self.failure or self.exit)

    @property
    def status(self):
        if self.skipped:
            return 'SKIP'
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

    def __init__(self, parent, test, skip_on_failure=None, critical_tags=None):
        _ExecutionStatus.__init__(self, parent)
        self.exit = parent.exit
        self._skip_on_failure = self._should_skip_on_failure(
            test, skip_on_failure, critical_tags)

    def test_failed(self, failure):
        if self._skip_on_failure:
            self.failure.test = \
                 ("Test skipped with --SkipOnFailure, original error:\n%s"
                  % unic(failure))
            self.skipped = True
        else:
            self.failure.test = unic(failure)
            self.exit.failure_occurred(failure)

    def _should_skip_on_failure(self, test, skip_on_failure_tags,
                                critical_tags):
        # TODO: test if this can be used with not critical TagPattern
        critical_pattern = TagPatterns(critical_tags)
        if critical_pattern and critical_pattern.match(test.tags):
            return False
        skip_on_fail_pattern = TagPatterns(skip_on_failure_tags)
        return skip_on_fail_pattern and skip_on_fail_pattern.match(test.tags)

    def test_skipped(self, reason):
        self.skipped = True
        self.failure.test = unic(reason)

    def _my_message(self):
        return TestMessage(self).message


class _Message(object):
    setup_message = NotImplemented
    skipped_message = NotImplemented
    teardown_message = NotImplemented
    also_teardown_message = NotImplemented

    def __init__(self, status):
        self.failure = status.failure
        self.skipped = status.skipped

    @property
    def message(self):
        message = self._get_message_before_teardown()
        return self._get_message_after_teardown(message)

    def _get_message_before_teardown(self):
        if self.failure.setup:
            msg = self.setup_message if not self.skipped else self.skipped_message
            return self._format_setup_or_teardown_message(msg,
                                                          self.failure.setup)
        return self.failure.test or ''

    def _format_setup_or_teardown_message(self, prefix, message):
        if message.startswith('*HTML*'):
            prefix = '*HTML* ' + prefix
            message = message[6:].lstrip()
        return prefix % message

    def _get_message_after_teardown(self, message):
        if not self.failure.teardown:
            return message
        if not message:
            return self._format_setup_or_teardown_message(self.teardown_message,
                                                          self.failure.teardown)
        return self._format_message_with_teardown_message(message)

    def _format_message_with_teardown_message(self, message):
        teardown = self.failure.teardown
        if teardown.startswith('*HTML*'):
            teardown = teardown[6:].lstrip()
            if not message.startswith('*HTML*'):
                message = '*HTML* ' + html_escape(message)
        elif message.startswith('*HTML*'):
            teardown = html_escape(teardown)
        return self.also_teardown_message % (message, teardown)


class TestMessage(_Message):
    setup_message = 'Setup failed:\n%s'
    teardown_message = 'Teardown failed:\n%s'
    skipped_message = '%s'
    also_teardown_message = '%s\n\nAlso teardown failed:\n%s'
    exit_on_fatal_message = 'Test execution stopped due to a fatal error.'
    exit_on_failure_message = \
        'Failure occurred and exit-on-failure mode is in use.'
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
    # TODO: wording
    skipped_message = 'Skipped in suite setup:\n%s'
    teardown_message = 'Suite teardown failed:\n%s'
    also_teardown_message = '%s\n\nAlso suite teardown failed:\n%s'


class ParentMessage(SuiteMessage):
    setup_message = 'Parent suite setup failed:\n%s'
    skipped_message = 'Skipped in parent suite setup:\n%s'
    teardown_message = 'Parent suite teardown failed:\n%s'
    also_teardown_message = '%s\n\nAlso parent suite teardown failed:\n%s'

    def __init__(self, status):
        while status.parent and status.parent.failures:
            status = status.parent
        SuiteMessage.__init__(self, status)
