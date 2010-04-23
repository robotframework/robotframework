#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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

from robot import utils
from robot.common import BaseTestSuite, BaseTestCase
from robot.parsing import TestSuiteData
from robot.errors import ExecutionFailed
from robot.variables import GLOBAL_VARIABLES
from robot.output import LOGGER

from fixture import Setup, Teardown
from timeouts import TestTimeout
from keywords import KeywordFactory
from namespace import Namespace
from userkeyword import UserLibrary


def TestSuite(datasources, settings):
    suitedata = TestSuiteData(datasources, settings['SuiteNames'])
    suite = RunnableTestSuite(suitedata)
    suite.set_options(settings)
    return suite


class RunnableTestSuite(BaseTestSuite):

    def __init__(self, data, testdefaults=None, parent=None):
        BaseTestSuite.__init__(self, data.name, data.source, parent)
        self.variables = GLOBAL_VARIABLES.copy()
        self.variables.set_from_variable_table(data.variables)
        self.source = data.source
        self.doc = data.doc or ''
        self.metadata = data.metadata
        self.imports = data.imports
        self.user_keywords = UserLibrary(data.user_keywords)
        self.setup = data.suite_setup or []
        self.teardown = data.suite_teardown or []
        if not testdefaults:
            testdefaults = _TestCaseDefaults()
        testdefaults.add_defaults(data)
        for suite in data.suites:
            RunnableTestSuite(suite, testdefaults.copy(), parent=self)
        for test in data.tests:
            RunnableTestCase(test, testdefaults, parent=self)
        self._run_mode_exit_on_failure = False
        self.exit_requiring_err_occured = False

    def run(self, output, parent=None, errors=None):
        self._start_run(output, parent, errors)
        self._run_setup(output)
        self._run_sub_suites(output)
        self._run_tests(output)
        self._report_status(output)
        self._run_teardown(output)
        self._end_run(output)

    def _start_run(self, output, parent, errors):
        if not errors:
            errors = _SuiteRunErrors(self._run_mode_exit_on_failure)
        self._run_errors = errors
        self._run_errors.start_suite()
        self._init_run(parent)
        self._set_variable_dependent_metadata(self.namespace.variables)
        output.start_suite(self)

    def _init_run(self, parent):
        self.status = 'RUNNING'
        self.starttime = utils.get_timestamp()
        self.namespace = Namespace(self, parent)
        self.namespace.variables['${SUITE_NAME}'] = self.longname
        self.namespace.variables['${SUITE_SOURCE}'] = self.source

    def _set_variable_dependent_metadata(self, variables):
        errors = []
        self.doc = variables.replace_meta('Documentation', self.doc, errors)
        self.setup = Setup(variables.replace_meta('Setup', self.setup, errors))
        self.teardown = Teardown(
            variables.replace_meta('Teardown', self.teardown, errors))
        for name, value in self.metadata.items():
            self.metadata[name] = variables.replace_meta(name, value, errors)
        if errors:
            self._run_errors.suite_init_err('Suite initialization failed:\n%s'
                                            % '\n'.join(errors))

    def _run_setup(self, output):
        if self._run_errors.is_suite_setup_allowed():
            self._run_errors.suite_setup_err(self._run_fixture(self.setup, output))

    def _run_teardown(self, output):
        if self._run_errors.is_suite_teardown_allowed():
            td_err = self._run_fixture(self.teardown, output)
            if td_err:
                self.suite_teardown_failed('Suite teardown failed:\n%s' % td_err)

    def _run_fixture(self, fixture, output):
        if fixture:
            try:
                fixture.run(output, self.namespace)
            except ExecutionFailed:
                return utils.get_error_message()
        return None

    def _run_sub_suites(self, output):
        for suite in self.suites:
            suite.run(output, self, self._run_errors)
            if suite.critical_stats.failed:
                self._run_errors.critical_failure()

    def _run_tests(self, output):
        executed_tests = []
        for test in self.tests:
            normname = utils.normalize(test.name)
            if normname in executed_tests:
                LOGGER.warn("Multiple test cases with name '%s' executed in "
                            "test suite '%s'"% (test.name, self.longname))
            executed_tests.append(normname)
            test.run(output, self.namespace, self._run_errors)
            if test.status == 'FAIL' and test.critical == 'yes':
                self._run_errors.critical_failure()
            self._set_prev_test_variables(self.namespace.variables, test)

    def _report_status(self, output):
        self.set_status()
        self.message = self._run_errors.suite_error()
        self.namespace.variables['${SUITE_STATUS}'] = self.status
        self.namespace.variables['${SUITE_MESSAGE}'] = self.get_full_message()

    def _end_run(self, output):
        self.endtime = utils.get_timestamp()
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)
        self._set_prev_test_variables(GLOBAL_VARIABLES, varz=self.namespace.variables)
        output.end_suite(self)
        self.namespace.end_suite()
        self._run_errors.end_suite()

    def _set_prev_test_variables(self, destination, test=None, varz=None):
        if test:
            name, status, message = test.name, test.status, test.message
        else:
            name, status, message = varz['${PREV_TEST_NAME}'], \
                    varz['${PREV_TEST_STATUS}'], varz['${PREV_TEST_MESSAGE}']
        destination['${PREV_TEST_NAME}'] = name
        destination['${PREV_TEST_STATUS}'] = status
        destination['${PREV_TEST_MESSAGE}'] = message


class _SuiteRunErrors(object):
    NO_ERROR = None
    _exit_on_failure_error = ('Critical failure occurred and ExitOnFailure '
                              'option is in use')
    _exit_on_fatal_error = 'Test execution is stopped due to a fatal error'

    def __init__(self, run_mode_is_exit_on_failure=False):
        self._run_mode_is_exit_on_failure = run_mode_is_exit_on_failure
        self._earlier_init_errors = []
        self._earlier_setup_errors = []
        self._earlier_suite_setup_executions = []
        self._init_current_errors()
        self._exit = self._fatal = False
        self._current_suite_setup_executed = False

    def _init_current_errors(self):
        self._current_init_err = self._current_setup_err = self.NO_ERROR

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
        return self._current_init_err is self.NO_ERROR and \
                not self._earlier_errors()

    def is_suite_teardown_allowed(self):
        if self._current_suite_setup_executed:
            return True
        return self._current_init_err is self.NO_ERROR and \
                not self._earlier_errors()

    def _earlier_errors(self):
        if self._fatal or self._exit:
            return True
        for err in self._earlier_setup_errors + self._earlier_init_errors:
            if err is not self.NO_ERROR:
                return True
        return False

    def suite_init_err(self, err):
        self._current_init_err = err

    def suite_setup_err(self, err):
        self._current_suite_setup_executed = True
        self._current_setup_err = err or self.NO_ERROR

    def suite_error(self):
        if self._earlier_init_erros_occurred():
            return 'Initialization of the parent suite failed.'
        if self._earlier_setup_errors_occurred():
            return 'Setup of the parent suite failed.'
        if self._current_init_err:
            return self._current_init_err
        if self._current_setup_err:
            return 'Suite setup failed:\n%s' % self._current_setup_err
        return ''

    def _earlier_init_erros_occurred(self):
        return bool([err for err in self._earlier_init_errors if err])

    def _earlier_setup_errors_occurred(self):
        return bool([err for err in self._earlier_setup_errors if err])

    def child_error(self):
        if self._current_init_err or self._earlier_init_erros_occurred():
            return 'Initialization of the parent suite failed.'
        if self._current_setup_err or self._earlier_setup_errors_occurred():
            return 'Setup of the parent suite failed.'
        if self._exit:
            return self._exit_on_failure_error
        if self._fatal:
            return self._exit_on_fatal_error
        return None

    def critical_failure(self):
        if self._run_mode_is_exit_on_failure:
            self._exit = True

    def fatal_error(self):
        self._fatal = True


class RunnableTestCase(BaseTestCase):

    def __init__(self, data, defaults, parent):
        BaseTestCase.__init__(self, data.name, parent)
        self.doc = data.doc or ''
        self.setup = utils.get_not_none(data.setup, defaults.test_setup)
        self.teardown = utils.get_not_none(data.teardown,
                                           defaults.test_teardown)
        self.tags = defaults.force_tags \
                    + utils.get_not_none(data.tags, defaults.default_tags)
        self.timeout = utils.get_not_none(data.timeout, defaults.test_timeout)
        self.keywords = [ KeywordFactory(kw) for kw in data.keywords ]
        self.exit_on_failure = False

    def run(self, output, namespace, suite_errors):
        self._suite_errors = suite_errors
        self._start_run(output, namespace, suite_errors)
        if not self._run_preventing_errors():
            self._run(output, namespace)
        else:
            self._run_failed()
        self._end_run(output, namespace)

    def _start_run(self, output, namespace, suite_errors):
        self._run_errors = _TestRunErrors(suite_errors)
        self.status = 'RUNNING'
        self.starttime = utils.get_timestamp()
        self._run_errors.init_err(self._init_test(namespace.variables))
        namespace.start_test(self)
        output.start_test(self)

    def _init_test(self, varz):
        errors = []
        self.doc = varz.replace_meta('Documentation', self.doc, errors)
        self.setup = Setup(varz.replace_meta('Setup', self.setup, errors))
        self.teardown = Teardown(
            varz.replace_meta('Teardown', self.teardown, errors))
        self.tags = utils.normalize_tags(
            varz.replace_meta('Tags', self.tags, errors))
        self.timeout = TestTimeout(
            *varz.replace_meta('Timeout', self.timeout, errors))
        if errors:
            return 'Test case initialization failed:\n%s' % '\n'.join(errors)
        if not self.keywords:
            return 'Test case contains no keywords'

    def _run_preventing_errors(self):
        return self._run_errors.parent_errors()

    def _run(self, output, namespace):
        self.init_ctx(namespace)
        self.timeout.start()
        self._run_setup(output, namespace)
        self._run_keywords(output, namespace)
        self._report_status(namespace)
        self._run_teardown(output, namespace)
        self._report_status_after_teardown()

    def init_ctx(self, namespace):
        namespace.variables['${TEST_NAME}'] = self.name
        namespace.variables['@{TEST_TAGS}'] = self.tags

    def _run_setup(self, output, namespace):
        setup_err = self._run_fixture(self.setup, output, namespace)
        self._run_errors.setup_err(setup_err)
        return self._run_errors.is_setup_err()

    def _run_keywords(self, output, namespace):
        if self._run_errors.is_setup_err():
            return
        for kw in self.keywords:
            kw_err = self._run_with_error_handling(kw, output, namespace)
            if kw_err:
                self._run_errors.kw_err(kw_err)
                return

    def _report_status(self, namespace):
        self.message = self._run_errors.get_message()
        namespace.variables['${TEST_MESSAGE}'] = self.message
        self.status = self.message == '' and 'PASS' or 'FAIL'
        namespace.variables['${TEST_STATUS}'] = self.status

    def _run_teardown(self, output, namespace):
        td_err = self._run_fixture(self.teardown, output, namespace)
        self._run_errors.teardown_err(td_err)

    def _report_status_after_teardown(self):
        if self._run_errors.is_teardown_err():
            self.status = 'FAIL'
            self.message = self._run_errors.get_teardown_error_msg(self.message)
        if self.status == 'PASS' and self.timeout.timed_out():
            self.status = 'FAIL'
            self.message = self.timeout.get_message()

    def _run_failed(self):
        self.status = 'FAIL'
        self.message = self._run_errors.orig_or_init_error()

    def _end_run(self, output, namespace):
        self.endtime = utils.get_timestamp()
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)
        output.end_test(self)
        namespace.end_test()

    def _run_fixture(self, fixture, output, namespace):
        if fixture:
            return self._run_with_error_handling(fixture, output, namespace)

    def _run_with_error_handling(self, runnable, output, namespace):
        try:
            runnable.run(output, namespace)
        except ExecutionFailed, err:
            self.timeout.set_keyword_timeout(err.timeout)
            if err.exit:
                self._suite_errors.fatal_error()
            return err.msg


class _TestRunErrors(object):

    def __init__(self, err):
        self._parent_err = err.child_error() if err else None
        self._init_err = None
        self._setup_err = None
        self._kw_err = None
        self._teardown_err = None

    def parent_errors(self):
        return bool(self._parent_err or self._init_err)

    def init_err(self, err):
        self._init_err = err

    def setup_err(self, err):
        self._setup_err = err

    def is_setup_err(self):
        return bool(self._setup_err)

    def kw_err(self, err):
        self._kw_err = err

    def teardown_err(self, err):
        self._teardown_err = err

    def is_teardown_err(self):
        return bool(self._teardown_err)

    def get_message(self):
        if self._setup_err:
            return 'Setup failed:\n%s' % self._setup_err
        return self._kw_err or ''

    def get_teardown_error_msg(self, message):
        if message == '':
            return 'Teardown failed:\n%s' % self._teardown_err
        return '%s\n\nAlso teardown failed:\n%s' % (message, self._teardown_err)

    def orig_or_init_error(self):
        return self._parent_err or self._init_err


class _TestCaseDefaults:

    def __init__(self):
        self.force_tags = []
        self.default_tags = []
        self.test_setup = []
        self.test_teardown = []
        self.test_timeout = []

    def add_defaults(self, suite):
        if suite.force_tags:
            self.force_tags.extend(suite.force_tags)
        if suite.default_tags:
            self.default_tags = suite.default_tags
        if suite.test_setup:
            self.test_setup = suite.test_setup
        if suite.test_teardown:
            self.test_teardown = suite.test_teardown
        if suite.test_timeout:
            self.test_timeout = suite.test_timeout

    def copy(self):
        copy = _TestCaseDefaults()
        copy.force_tags = self.force_tags[:]
        copy.default_tags = self.default_tags[:]
        copy.test_setup = self.test_setup[:]
        copy.test_teardown = self.test_teardown[:]
        copy.test_timeout = self.test_timeout[:]
        return copy

