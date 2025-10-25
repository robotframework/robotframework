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

from abc import ABC

from robot.errors import PassExecution
from robot.model import TagPatterns
from robot.utils import html_escape, plural_or_not as s, seq2str, test_or_task


class Failure:

    def __init__(self):
        self.setup = None
        self.test = None
        self.teardown = None
        self.setup_skipped = None
        self.test_skipped = None
        self.teardown_skipped = None

    def __bool__(self):
        return (
            self.setup is not None
            or self.test is not None
            or self.teardown is not None
            or self.setup_skipped is not None
            or self.test_skipped is not None
            or self.teardown_skipped is not None
        )


class Exit:

    def __init__(self, failure_mode=False, error_mode=False, skip_teardown_mode=False):
        self.failure_mode = failure_mode
        self.error_mode = error_mode
        self.skip_teardown_mode = skip_teardown_mode
        self.failure = False
        self.error = False
        self.fatal = False

    def failure_occurred(self, fatal=False, suite_setup=False):
        if fatal:
            self.fatal = True
        if self.failure_mode and not suite_setup:
            self.failure = True

    def error_occurred(self):
        if self.error_mode:
            self.error = True

    @property
    def teardown_allowed(self):
        return not (self.skip_teardown_mode and self)

    def __bool__(self):
        return bool(self.failure or self.error or self.fatal)


class ExecutionStatus(ABC):

    def __init__(self, parent, exit=None):
        self.parent = parent
        self.exit = exit if exit is not None else parent.exit
        self.failure = Failure()
        self.skipped = False
        self._teardown_allowed = False

    @property
    def failed(self):
        return bool(self.parent and self.parent.failed or self.failure or self.exit)

    @property
    def passed(self):
        return not self.failed

    def setup_executed(self, error=None):
        if error and not isinstance(error, PassExecution):
            msg = str(error)
            if error.skip:
                self.failure.setup_skipped = msg
                self.skipped = True
            elif self._skip_on_failure():
                self.failure.test = self._skip_on_fail_msg(f"Setup failed:\n{msg}")
                self.skipped = True
            else:
                self.failure.setup = msg
                self.exit.failure_occurred(
                    error.exit, suite_setup=isinstance(self, SuiteStatus)
                )
        self._teardown_allowed = True

    def teardown_executed(self, error=None):
        if error and not isinstance(error, PassExecution):
            msg = str(error)
            if error.skip:
                self.failure.teardown_skipped = msg
                self.skipped = True
            elif self._skip_on_failure():
                self.failure.test = self._skip_on_fail_msg(f"Teardown failed:\n{msg}")
                self.skipped = True
            else:
                self.failure.teardown = msg
                self.exit.failure_occurred(error.exit)

    def failure_occurred(self):
        self.exit.failure_occurred()

    def error_occurred(self):
        self.exit.error_occurred()

    @property
    def teardown_allowed(self):
        return self.exit.teardown_allowed and self._teardown_allowed

    @property
    def status(self):
        if self.skipped or (self.parent and self.parent.skipped):
            return "SKIP"
        if self.failed:
            return "FAIL"
        return "PASS"

    def _skip_on_failure(self):
        return False

    def _skip_on_fail_msg(self, msg):
        return msg

    @property
    def message(self):
        if self.failure or self.exit:
            return self._my_message()
        if self.parent and not self.parent.passed:
            return self._parent_message()
        return ""

    def _my_message(self):
        raise NotImplementedError

    def _parent_message(self):
        return ParentMessage(self.parent).message


class SuiteStatus(ExecutionStatus):

    def __init__(
        self,
        parent=None,
        exit_on_failure=False,
        exit_on_error=False,
        skip_teardown_on_exit=False,
    ):
        if parent is None:
            exit = Exit(exit_on_failure, exit_on_error, skip_teardown_on_exit)
        else:
            exit = None
        super().__init__(parent, exit)

    def _my_message(self):
        return SuiteMessage(self).message


class TestStatus(ExecutionStatus):

    def __init__(self, parent, test, skip_on_failure=(), rpa=False):
        super().__init__(parent)
        self.test = test
        self.skip_on_failure_tags = TagPatterns(skip_on_failure)
        self.rpa = rpa

    def test_failed(self, message=None, error=None):
        if error is not None:
            message = str(error)
            skip = error.skip
            fatal = error.exit or self.test.tags.robot("exit-on-failure")
        else:
            skip = fatal = False
        if skip:
            self.test_skipped(message)
        elif self._skip_on_failure():
            self.failure.test = self._skip_on_fail_msg(message)
            self.skipped = True
        else:
            self.failure.test = message
            self.exit.failure_occurred(fatal)

    def test_skipped(self, message):
        self.skipped = True
        self.failure.test_skipped = message

    @property
    def skip_on_failure_after_tag_changes(self):
        if not self.skipped and self.failed and self._skip_on_failure():
            self.failure.test = self._skip_on_fail_msg(self.failure.test)
            self.skipped = True
            return True
        return False

    def _skip_on_failure(self):
        tags = self.test.tags
        return tags.robot("skip-on-failure") or self.skip_on_failure_tags.match(tags)

    def _skip_on_fail_msg(self, fail_msg):
        if self.test.tags.robot("skip-on-failure"):
            tags = ["robot:skip-on-failure"]
            kind = "tag"
        else:
            tags = self.skip_on_failure_tags
            kind = "tag" if tags.is_constant else "tag pattern"
        return test_or_task(
            f"Failed {{test}} skipped using {seq2str(tags)} {kind}{s(tags)}.\n\n"
            f"Original failure:\n{fail_msg}",
            rpa=self.rpa,
        )

    def _my_message(self):
        return TestMessage(self).message


class Message(ABC):
    setup_message = ""
    setup_skipped_message = ""
    teardown_skipped_message = ""
    teardown_message = ""
    also_teardown_message = ""
    also_teardown_skip_message = ""

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
                self.setup_skipped_message, self.failure.setup_skipped
            )
        if self.failure.setup:
            return self._format_setup_or_teardown_message(
                self.setup_message, self.failure.setup
            )
        return self.failure.test_skipped or self.failure.test or ""

    def _format_setup_or_teardown_message(self, prefix, message):
        if message.startswith("*HTML*"):
            prefix = "*HTML* " + prefix
            message = message[6:].lstrip()
        return prefix % message

    def _get_message_after_teardown(self, message):
        if not (self.failure.teardown or self.failure.teardown_skipped):
            return message
        if not message:
            if self.failure.teardown:
                prefix, msg = self.teardown_message, self.failure.teardown
            else:
                prefix, msg = (
                    self.teardown_skipped_message,
                    self.failure.teardown_skipped,
                )
            return self._format_setup_or_teardown_message(prefix, msg)
        return self._format_message_with_teardown_message(message)

    def _format_message_with_teardown_message(self, message):
        teardown = self.failure.teardown or self.failure.teardown_skipped
        if teardown.startswith("*HTML*"):
            teardown = teardown[6:].lstrip()
            if not message.startswith("*HTML*"):
                message = "*HTML* " + html_escape(message)
        elif message.startswith("*HTML*"):
            teardown = html_escape(teardown)
        if self.failure.teardown:
            return self.also_teardown_message % (message, teardown)
        return self.also_teardown_skip_message % (teardown, message)


class TestMessage(Message):
    setup_message = "Setup failed:\n%s"
    teardown_message = "Teardown failed:\n%s"
    setup_skipped_message = "%s"
    teardown_skipped_message = "%s"
    also_teardown_message = "%s\n\nAlso teardown failed:\n%s"
    also_teardown_skip_message = "Skipped in teardown:\n%s\n\nEarlier message:\n%s"
    exit_on_fatal_message = "Test execution stopped due to a fatal error."
    exit_on_failure_message = "Failure occurred and exit-on-failure mode is in use."
    exit_on_error_message = "Error occurred and exit-on-error mode is in use."

    def __init__(self, status):
        super().__init__(status)
        self.exit = status.exit

    @property
    def message(self):
        message = super().message
        if message:
            return message
        if self.exit.failure:
            return self.exit_on_failure_message
        if self.exit.fatal:
            return self.exit_on_fatal_message
        if self.exit.error:
            return self.exit_on_error_message
        return ""


class SuiteMessage(Message):
    setup_message = "Suite setup failed:\n%s"
    setup_skipped_message = "Skipped in suite setup:\n%s"
    teardown_skipped_message = "Skipped in suite teardown:\n%s"
    teardown_message = "Suite teardown failed:\n%s"
    also_teardown_message = "%s\n\nAlso suite teardown failed:\n%s"
    also_teardown_skip_message = (
        "Skipped in suite teardown:\n%s\n\nEarlier message:\n%s"
    )


class ParentMessage(SuiteMessage):
    setup_message = "Parent suite setup failed:\n%s"
    setup_skipped_message = "Skipped in parent suite setup:\n%s"
    teardown_skipped_message = "Skipped in parent suite teardown:\n%s"
    teardown_message = "Parent suite teardown failed:\n%s"
    also_teardown_message = "%s\n\nAlso parent suite teardown failed:\n%s"

    def __init__(self, status):
        while status.parent and status.parent.failed:
            status = status.parent
        super().__init__(status)
