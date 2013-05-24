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


class TestFailures(object):

    def __init__(self):
        self.setup_failure = None
        self.test_failure = None
        self.teardown_failure = None

    @property
    def run_allowed(self):
        return self.setup_failure is None

    @property
    def message(self):
        msg = self._get_message_before_teardown()
        return self._get_message_after_teardown(msg)

    def _get_message_before_teardown(self):
        if self.setup_failure is not None:
            return 'Setup failed:\n%s' % self.setup_failure
        return self.test_failure or ''

    def _get_message_after_teardown(self, msg):
        if self.teardown_failure is None:
            return msg
        if not msg:
            return 'Teardown failed:\n%s' % self.teardown_failure
        return '%s\n\nAlso teardown failed:\n%s' % (msg, self.teardown_failure)

    def __nonzero__(self):
        return (self.setup_failure is not None or
                self.test_failure is not None or
                self.teardown_failure is not None)
