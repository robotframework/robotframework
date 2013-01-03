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

class SuiteRunErrors(object):
    _exit_on_failure_error = ('Critical failure occurred and ExitOnFailure '
                              'option is in use')
    _exit_on_fatal_error = 'Test execution is stopped due to a fatal error'
    _parent_suite_init_error = 'Initialization of the parent suite failed.'
    _parent_suite_setup_error = 'Setup of the parent suite failed:\n'

    def __init__(self, exit_on_failure_mode=False, skip_teardowns_on_exit_mode=False):
        self._exit_on_failure_mode = exit_on_failure_mode
        self._skip_teardowns_on_exit_mode = skip_teardowns_on_exit_mode
        self._earlier_init_errors = []
        self._earlier_setup_errors = []
        self._earlier_setup_executions = []
        self._init_error = None
        self._setup_error = None
        self._setup_executed = False
        self._exit_on_failure = False
        self._exit_on_fatal = False

    @property
    def exit(self):
        return self._exit_on_fatal or self._exit_on_failure

    def start_suite(self):
        self._earlier_init_errors.append(self._init_error)
        self._earlier_setup_errors.append(self._setup_error)
        self._earlier_setup_executions.append(self._setup_executed)
        self._init_error = None
        self._setup_error = None
        self._setup_executed = False

    def end_suite(self):
        self._setup_error = self._earlier_setup_errors.pop()
        self._init_error = self._earlier_init_errors.pop()
        self._setup_executed = self._earlier_setup_executions.pop()

    def is_suite_setup_allowed(self):
        return not (self._init_error or self.exit or
                    any(self._earlier_init_errors + self._earlier_setup_errors))

    def is_suite_teardown_allowed(self):
        return self._setup_executed and not self._skip_teardown()

    def _skip_teardown(self):
        return self._skip_teardowns_on_exit_mode and self.exit

    def is_test_teardown_allowed(self):
        return not self._skip_teardown()

    def suite_initialized(self, error=None):
        if error:
            self._init_error = 'Suite initialization failed:\n%s' % error

    def setup_executed(self, error=None):
        self._setup_executed = True
        if error:
            self._setup_error = unicode(error)
            if error.exit:
                self._exit_on_fatal = True

    def get_suite_error(self):
        if self._init_error:
            return self._init_error
        if self._setup_error:
            return 'Suite setup failed:\n%s' % self._setup_error
        if any(self._earlier_init_errors):
            return self._parent_suite_init_error
        if any(self._earlier_setup_errors):
            return self._get_setup_error()
        return None

    def get_child_error(self):
        if self._init_error or any(self._earlier_init_errors):
            return self._parent_suite_init_error
        if self._setup_error or any(self._earlier_setup_errors):
            return self._get_setup_error()
        if self._exit_on_failure:
            return self._exit_on_failure_error
        if self._exit_on_fatal:
            return self._exit_on_fatal_error
        return None

    def _get_setup_error(self):
        error = self._setup_error or [e for e in self._earlier_setup_errors if e][0]
        return self._parent_suite_setup_error + error

    def test_failed(self, exit=False, critical=False):
        if critical and self._exit_on_failure_mode:
            self._exit_on_failure = True
        if exit:
            self._exit_on_fatal = True


class TestRunErrors(object):

    def __init__(self, parent):
        self._parent = parent
        self._parent_error = parent.get_child_error()
        self._init_error = None
        self._setup_error = None
        self._keyword_error = None
        self._teardown_error = None

    def is_allowed_to_run(self):
        return not bool(self._parent_error or self._init_error)

    def is_test_teardown_allowed(self):
        return self._parent.is_test_teardown_allowed()

    def test_initialized(self, error=None):
        self._init_error = error

    def setup_failed(self, error):
        self._setup_error = unicode(error)

    def keyword_failed(self, error):
        self._keyword_error = unicode(error)

    def teardown_failed(self, error):
        self._teardown_error = unicode(error)

    def test_failed(self, exit=False, critical=False):
        self._parent.test_failed(exit, critical)

    def get_message(self):
        if self._setup_error:
            return 'Setup failed:\n%s' % self._setup_error
        return self._keyword_error

    def get_teardown_message(self, message):
        if not message:
            return 'Teardown failed:\n%s' % self._teardown_error
        return '%s\n\nAlso teardown failed:\n%s' % (message, self._teardown_error)

    def get_parent_or_init_error(self):
        return self._parent_error or self._init_error
