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
from runerrors import SuiteRunErrors, TestRunErrors
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
            errors = SuiteRunErrors(self._run_mode_exit_on_failure)
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

    def _run_tests(self, output):
        executed_tests = []
        for test in self.tests:
            normname = utils.normalize(test.name)
            if normname in executed_tests:
                LOGGER.warn("Multiple test cases with name '%s' executed in "
                            "test suite '%s'"% (test.name, self.longname))
            executed_tests.append(normname)
            test.run(output, self.namespace, self._run_errors)
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
        self._start_run(output, namespace)
        if self._run_errors.is_allowed_to_run():
            self._run(output, namespace)
        else:
            self._not_allowed_to_run()
        self._end_run(output, namespace)

    def _start_run(self, output, namespace):
        self._run_errors = TestRunErrors(self._suite_errors)
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

    def _run(self, output, namespace):
        self.init_ctx(namespace)
        self.timeout.start()
        self._run_setup(output, namespace)
        if not self._run_errors.setup_failed():
            self._run_keywords(output, namespace)
        self._report_status(namespace)
        self._run_teardown(output, namespace)
        self._report_status_after_teardown()

    def init_ctx(self, namespace):
        namespace.variables['${TEST_NAME}'] = self.name
        namespace.variables['@{TEST_TAGS}'] = self.tags

    def _run_setup(self, output, namespace):
        error = self._run_fixture(self.setup, output, namespace)
        if error:
            self._run_errors.setup_err(error.msg)

    def _run_keywords(self, output, namespace):
        for kw in self.keywords:
            error = self._run_with_error_handling(kw, output, namespace)
            if error:
                self._run_errors.kw_err(error.msg)
                if not error.cont:
                    return

    def _report_status(self, namespace):
        message = self._run_errors.get_message()
        if message:
            self.status = 'FAIL'
            self.message = message
        else:
            self.status = 'PASS'
        namespace.variables['${TEST_MESSAGE}'] = self.message
        namespace.variables['${TEST_STATUS}'] = self.status

    def _run_teardown(self, output, namespace):
        error = self._run_fixture(self.teardown, output, namespace)
        if error:
            self._run_errors.teardown_err(error.msg)

    def _report_status_after_teardown(self):
        if self._run_errors.teardown_failed():
            self.status = 'FAIL'
            self.message = self._run_errors.get_teardown_message(self.message)
        if self.status == 'PASS' and self.timeout.timed_out():
            self.status = 'FAIL'
            self.message = self.timeout.get_message()
        if self.status == 'FAIL':
            self._suite_errors.test_failed(critical=self.critical=='yes')

    def _not_allowed_to_run(self):
        self.status = 'FAIL'
        self.message = self._run_errors.parent_or_init_error()

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
            return None
        except ExecutionFailed, err:
            self.timeout.set_keyword_timeout(err.timeout)
            self._suite_errors.test_failed(exit=err.exit)
            return err


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
