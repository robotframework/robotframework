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
    _NO_ERROR = None
    _exit_on_failure_error = ('Critical failure occurred and ExitOnFailure '
                              'option is in use')
    _exit_on_fatal_error = 'Test execution is stopped due to a fatal error'
    _parent_suite_init_error = 'Initialization of the parent suite failed.'
    _parent_suite_setup_error = 'Setup of the parent suite failed.'

    def __init__(self, run_mode_is_exit_on_failure=False, run_mode_skip_teardowns_on_exit=False):
        self._run_mode_is_exit_on_failure = run_mode_is_exit_on_failure
        self._run_mode_skip_teardowns_on_exit = run_mode_skip_teardowns_on_exit
        self._earlier_init_errors = []
        self._earlier_setup_errors = []
        self._earlier_suite_setup_executions = []
        self._init_current_errors()
        self._exit_runmode = self._exit_fatal = False
        self._current_suite_setup_executed = False

    @property
    def exit(self):
        return self._exit_fatal or self._exit_runmode

    def _init_current_errors(self):
        self._current_init_err = self._current_setup_err = self._NO_ERROR

    def start_suite(self):
        self._earlier_init_errors.append(self._current_init_err)
        self._earlier_setup_errors.append(self._current_setup_err)
        self._earlier_suite_setup_executions.append(self._current_suite_setup_executed)
        self._init_current_errors()
        self._current_suite_setup_executed = False

    def end_suite(self):
        self._current_setup_err = self._earlier_setup_errors.pop()
        self._current_init_err = self._earlier_init_errors.pop()
        self._current_suite_setup_executed = self._earlier_suite_setup_executions.pop()

    def is_suite_setup_allowed(self):
        return self._current_init_err is self._NO_ERROR and \
                not self._earlier_errors()

    def is_suite_teardown_allowed(self):
        if not self.is_test_teardown_allowed():
            return False
        if self._current_suite_setup_executed:
            return True
        return self._current_init_err is self._NO_ERROR and \
                not self._earlier_errors()

    def is_test_teardown_allowed(self):
        if not self._run_mode_skip_teardowns_on_exit:
            return True
        return not (self._exit_fatal or self._exit_runmode)

    def _earlier_errors(self):
        if self._exit_runmode or self._exit_fatal:
            return True
        for err in self._earlier_setup_errors + self._earlier_init_errors:
            if err is not self._NO_ERROR:
                return True
        return False

    def suite_init_err(self, error_message):
        self._current_init_err = error_message

    def setup_executed(self):
        self._current_suite_setup_executed = True

    def suite_setup_err(self, err):
        if err.exit:
            self._exit_fatal = True
        self._current_setup_err = unicode(err)

    def suite_error(self):
        if self._earlier_init_erros_occurred():
            return self._parent_suite_init_error
        if self._earlier_setup_errors_occurred():
            return self._parent_suite_setup_error
        if self._current_init_err:
            return self._current_init_err
        if self._current_setup_err:
            return 'Suite setup failed:\n%s' % self._current_setup_err
        return ''

    def _earlier_init_erros_occurred(self):
        return any(self._earlier_init_errors)

    def _earlier_setup_errors_occurred(self):
        return any(self._earlier_setup_errors)

    def child_error(self):
        if self._current_init_err or self._earlier_init_erros_occurred():
            return self._parent_suite_init_error
        if self._current_setup_err or self._earlier_setup_errors_occurred():
            return self._parent_suite_setup_error
        if self._exit_runmode:
            return self._exit_on_failure_error
        if self._exit_fatal:
            return self._exit_on_fatal_error
        return None

    def test_failed(self, exit=False, critical=False):
        if critical and self._run_mode_is_exit_on_failure:
            self._exit_runmode = True
        if exit:
            self._exit_fatal = True


class TestRunErrors(object):

    def __init__(self, err):
        self._parent_err = err.child_error() if err else None
        self._init_err = None
        self._setup_err = None
        self._kw_err = None
        self._teardown_err = None

    def is_allowed_to_run(self):
        return not bool(self._parent_err or self._init_err)

    def init_err(self, err):
        self._init_err = err

    def setup_err(self, err):
        self._setup_err = err

    def setup_failed(self):
        return bool(self._setup_err)

    def kw_err(self, error):
        self._kw_err = error

    def teardown_err(self, err):
        self._teardown_err = err

    def teardown_failed(self):
        return bool(self._teardown_err)

    def get_message(self):
        if self._setup_err:
            return 'Setup failed:\n%s' % self._setup_err
        return self._kw_err

    def get_teardown_message(self, message):
        if message == '':
            return 'Teardown failed:\n%s' % self._teardown_err
        return '%s\n\nAlso teardown failed:\n%s' % (message, self._teardown_err)

    def parent_or_init_error(self):
        return self._parent_err or self._init_err


class KeywordRunErrors(object):

    def __init__(self):
        self.teardown_error = None

    def get_message(self):
        if not self._teardown_err:
            return self._kw_err
        if not self._kw_err:
            return 'Keyword teardown failed:\n%s' % self._teardown_err
        return '%s\n\nAlso keyword teardown failed:\n%s' % (self._kw_err,
                                                            self._teardown_err)



    def teardown_err(self, err):
        self.teardown_error = err

