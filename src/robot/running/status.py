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

from robot.errors import ExecutionStatus, PassExecution
from robot.model import TagPatterns
from robot.utils import html_escape, py3to2, unic, test_or_task


@py3to2
class Failure(object):

    def __init__(self):
        self.setup = None
        self.test = None
        self.teardown = None
        self.setup_skipped = None
        self.test_skipped = None
        self.teardown_skipped = None

    def __bool__(self):
        return bool(
            self.setup or self.test or self.teardown or
            self.setup_skipped or self.test_skipped or self.teardown_skipped
        )


@py3to2
class Exit(object):

    def __init__(self, failure_mode=False, error_mode=False, skip_teardown_mode=False):
        self.failure_mode = failure_mode
        self.error_mode = error_mode
        self.skip_teardown_mode = skip_teardown_mode
        self.failure = False
        self.error = False
        self.fatal = False

    def failure_occurred(self, failure=None):
        if isinstance(failure, ExecutionStatus) and failure.exit:
            self.fatal = True
        if self.failure_mode:
            self.failure = True

    def error_occurred(self):
        if self.error_mode:
            self.error = True

    @property
    def teardown_allowed(self):
        return not (self.skip_teardown_mode and self)

    def __bool__(self):
        return self.failure or self.error or self.fatal


class _ExecutionStatus(object):

    def __init__(self, parent=None, *exit_modes):
        self.parent = parent
        self.children = []
        self.failure = Failure()
        self.exit = parent.exit if parent else Exit(*exit_modes)
        self.skipped = False
        self._teardown_allowed = False
        self._rpa = False
        if parent:
            parent.children.append(self)

    def setup_executed(self, failure=None):
        if failure and not isinstance(failure, PassExecution):
            if failure.skip:
                self.failure.setup_skipped = unic(failure)
                self.skipped = True
            elif self._skip_on_failure():
                msg = self._skip_on_failure_message('Setup failed:\n%s' % failure)
                self.failure.test = msg
                self.skipped = True
            else:
                self.failure.setup = unic(failure)
                self.exit.failure_occurred(failure)

        self._teardown_allowed = True

    def teardown_executed(self, failure=None):
        if failure and not isinstance(failure, PassExecution):
            if failure.skip:
                self.failure.teardown_skipped = unic(failure)
                # Keep the Skip status in case the teardown failed
                self.skipped = self.skipped or failure.skip
            elif self._skip_on_failure():
                msg = self._skip_on_failure_message('Teardown failed:\n%s' % failure)
                self.failure.test = msg
                self.skipped = True
            else:
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
    def failed(self):
        return bool(self.parent and self.parent.failed or self.failure or self.exit)

    @property
    def status(self):
        if self.skipped or (self.parent and self.parent.skipped):
            return 'SKIP'
        if self.failed:
            return 'FAIL'
        return 'PASS'

    def _skip_on_failure(self):
        return False

    def _skip_on_failure_message(self, failure):
        return test_or_task(
            "{Test} failed but its tags matched '--SkipOnFailure' and it was marked "
            "skipped.\n\nOriginal failure:\n%s" % unic(failure), rpa=self._rpa
        )

    @property
    def message(self):
        if self.failure or self.exit:
            return self._my_message()
        if self.parent and self.parent.failed:
            return self._parent_message()
        return ''

    def _my_message(self):
        raise NotImplementedError

    def _parent_message(self):
        return ParentMessage(self.parent).message


class SuiteStatus(_ExecutionStatus):

    def __init__(self, parent=None, exit_on_failure_mode=False,
                 exit_on_error_mode=False, skip_teardown_on_exit_mode=False):
        _ExecutionStatus.__init__(self, parent, exit_on_failure_mode,
                                  exit_on_error_mode, skip_teardown_on_exit_mode)

    def _my_message(self):
        return SuiteMessage(self).message


class TestStatus(_ExecutionStatus):

    def __init__(self, parent, test, skip_on_failure=None, critical_tags=None,
                 rpa=False):
        _ExecutionStatus.__init__(self, parent)
        self.exit = parent.exit
        self._test = test
        self._skip_on_failure_tags = skip_on_failure
        self._critical_tags = critical_tags
        self._rpa = rpa

    def test_failed(self, failure):
        if hasattr(failure, 'skip') and failure.skip:
            self.test_skipped(failure)
        elif self._skip_on_failure():
            msg = self._skip_on_failure_message(failure)
            self.failure.test = msg
            self.skipped = True
        else:
            self.failure.test = unic(failure)
            self.exit.failure_occurred(failure)

    def test_skipped(self, reason):
        self.skipped = True
        self.failure.test_skipped = unic(reason)

    def skip_if_needed(self):
        if not self.skipped and self.failed and self._skip_on_failure():
            msg = self._skip_on_failure_message(self.failure.test)
            self.failure.test = msg
            self.skipped = True
            return True
        return False

    def _skip_on_failure(self):
        tags = self._test.tags
        critical_pattern = TagPatterns(self._critical_tags)
        critical = not critical_pattern or critical_pattern.match(tags)
        skip_on_fail_pattern = TagPatterns(self._skip_on_failure_tags)
        skip_on_fail = skip_on_fail_pattern and skip_on_fail_pattern.match(tags)
        return not critical or skip_on_fail

    def _my_message(self):
        return TestMessage(self).message


class _Message(object):
    setup_message = NotImplemented
    setup_skipped_message = NotImplemented
    teardown_skipped_message = NotImplemented
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
        if self.failure.setup_skipped:
            return self._format_setup_or_teardown_message(
                self.setup_skipped_message, self.failure.setup_skipped)
        if self.failure.setup:
            return self._format_setup_or_teardown_message(
                self.setup_message, self.failure.setup)
        return self.failure.test_skipped or self.failure.test or ''

    def _format_setup_or_teardown_message(self, prefix, message):
        if message.startswith('*HTML*'):
            prefix = '*HTML* ' + prefix
            message = message[6:].lstrip()
        return prefix % message

    def _get_message_after_teardown(self, message):
        if not (self.failure.teardown or self.failure.teardown_skipped):
            return message
        if not message:
            if self.failure.teardown:
                prefix, msg = self.teardown_message, self.failure.teardown
            else:
                prefix, msg = self.teardown_skipped_message, self.failure.teardown_skipped
            return self._format_setup_or_teardown_message(prefix, msg)
        return self._format_message_with_teardown_message(message)

    def _format_message_with_teardown_message(self, message):
        teardown = self.failure.teardown or self.failure.teardown_skipped
        if teardown.startswith('*HTML*'):
            teardown = teardown[6:].lstrip()
            if not message.startswith('*HTML*'):
                message = '*HTML* ' + html_escape(message)
        elif message.startswith('*HTML*'):
            teardown = html_escape(teardown)
        if self.failure.teardown:
            return self.also_teardown_message % (message, teardown)
        return self.also_teardown_skip_message % (teardown, message)


class TestMessage(_Message):
    setup_message = 'Setup failed:\n%s'
    teardown_message = 'Teardown failed:\n%s'
    setup_skipped_message = '%s'
    teardown_skipped_message = '%s'
    also_teardown_message = '%s\n\nAlso teardown failed:\n%s'
    also_teardown_skip_message = 'Skipped in teardown:\n%s\n\nEarlier message:\n%s'
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
    setup_skipped_message = 'Skipped in suite setup:\n%s'
    teardown_skipped_message = 'Skipped in suite teardown:\n%s'
    teardown_message = 'Suite teardown failed:\n%s'
    also_teardown_message = '%s\n\nAlso suite teardown failed:\n%s'
    also_teardown_skip_message = 'Skipped in suite teardown:\n%s\n\nEarlier message:\n%s'


class ParentMessage(SuiteMessage):
    setup_message = 'Parent suite setup failed:\n%s'
    setup_skipped_message = 'Skipped in parent suite setup:\n%s'
    teardown_skipped_message = 'Skipped in parent suite teardown:\n%s'
    teardown_message = 'Parent suite teardown failed:\n%s'
    also_teardown_message = '%s\n\nAlso parent suite teardown failed:\n%s'

    def __init__(self, status):
        while status.parent and status.parent.failed:
            status = status.parent
        SuiteMessage.__init__(self, status)
