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

    _exit_on_failure_error = ('Critical failure occurred and ExitOnFailure '
                              'option is in use')

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
        self._exit_on_failure = False

    def run(self, output, parent=None, error=None):
        self.status = 'RUNNING'
        self.starttime = utils.get_timestamp()
        self.namespace = Namespace(self, parent)
        self.namespace.variables['${SUITE_NAME}'] = self.longname
        init_err = self._init_suite(self.namespace.variables)
        output.start_suite(self)
        setup_err = self._run_fixture(self.setup, output, error, init_err)
        child_err = self._get_child_error(error, init_err, setup_err)
        for suite in self.suites:
            suite.run(output, self, child_err)
            if self._exit_on_failure and not child_err and \
                   suite.critical_stats.failed:
                child_err = self._exit_on_failure_error
        executed_tests = []
        for test in self.tests:
            normname = utils.normalize(test.name)
            if normname in executed_tests:
                LOGGER.warn("Multiple test cases with name '%s' executed in "
                            "test suite '%s'"% (test.name, self.longname))
            executed_tests.append(normname)
            test.run(output, self.namespace, child_err)
            if self._exit_on_failure and not child_err and \
                    test.status == 'FAIL' and test.critical == 'yes':
                child_err = self._exit_on_failure_error
            self._set_prev_test_variables(self.namespace.variables, test)
        self.set_status()
        self.message = self._get_my_error(error, init_err, setup_err)
        self.namespace.variables['${SUITE_STATUS}'] = self.status
        self.namespace.variables['${SUITE_MESSAGE}'] = self.get_full_message()
        td_err = self._run_fixture(self.teardown, output, error, init_err)
        if td_err:
            self.suite_teardown_failed('Suite teardown failed:\n%s' % td_err)
        self.endtime = utils.get_timestamp()
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)
        self._set_prev_test_variables(GLOBAL_VARIABLES,
                                      varz=self.namespace.variables)
        output.end_suite(self)
        self.namespace.end_suite()

    def _init_suite(self, varz):
        errors = []
        self.doc = varz.replace_meta('Documentation', self.doc, errors)
        self.setup = Setup(varz.replace_meta('Setup', self.setup, errors))
        self.teardown = Teardown(
            varz.replace_meta('Teardown', self.teardown, errors))
        for name, value in self.metadata.items():
            self.metadata[name] = varz.replace_meta(name, value, errors)
        if errors:
            return 'Suite initialization failed:\n%s' % '\n'.join(errors)

    def _get_child_error(self, error, init_error, setup_error):
        if error:
            return error
        if init_error:
            return 'Initialization of the parent suite failed.'
        if setup_error:
            return 'Setup of the parent suite failed.'
        return None

    def _get_my_error(self, error, init_error, setup_error):
        if error:
            return error
        if init_error:
            return init_error
        if setup_error:
            return 'Suite setup failed:\n%s' % setup_error
        return ''

    def _run_fixture(self, fixture, output, error, init_error):
        if fixture and not (error or init_error):
            try:
                fixture.run(output, self.namespace)
            except ExecutionFailed:
                return utils.get_error_message()

    def _set_prev_test_variables(self, destination, test=None, varz=None):
        if test is not None:
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

    def run(self, output, namespace, error=None):
        self.status = 'RUNNING'
        self.starttime = utils.get_timestamp()
        init_err = self._init_test(namespace.variables)
        error = error or init_err
        namespace.start_test(self)
        output.start_test(self)
        if not error:
            self._run(output, namespace)
        else:
            self.status = 'FAIL'
            self.message = error
        self.endtime = utils.get_timestamp()
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)
        output.end_test(self)
        namespace.end_test()

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
        namespace.variables['${TEST_NAME}'] = self.name
        namespace.variables['@{TEST_TAGS}'] = self.tags
        self.timeout.start()
        setup_err = self._run_fixture(self.setup, output, namespace)
        kw_err = self._run_keywords(output, namespace, setup_err)
        self.message = self._get_message(setup_err, kw_err)
        self.status = self.message == '' and 'PASS' or 'FAIL'
        namespace.variables['${TEST_STATUS}'] = self.status
        namespace.variables['${TEST_MESSAGE}'] = self.message
        td_err = self._run_fixture(self.teardown, output, namespace)
        if td_err:
            self.message = self._get_teardown_error(self.message, td_err)
            self.status = 'FAIL'
        if self.status == 'PASS' and self.timeout.timed_out():
            self.status = 'FAIL'
            self.message = self.timeout.get_message()

    def _run_fixture(self, fixture, output, namespace):
        if fixture:
            try:
                fixture.run(output, namespace)
            except ExecutionFailed:
                return utils.get_error_message()

    def _run_keywords(self, output, namespace, setup_err):
        if not setup_err:
            for kw in self.keywords:
                try:
                    kw.run(output, namespace)
                except ExecutionFailed:
                    return utils.get_error_message()

    def _get_message(self, setup_err, kw_err):
        if setup_err:
            return 'Setup failed:\n%s' % setup_err
        return kw_err or ''

    def _get_teardown_error(self, message, teardown_err):
        if message == '':
            return 'Teardown failed:\n%s' % teardown_err
        return '%s\n\nAlso teardown failed:\n%s' % (message, teardown_err)


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
