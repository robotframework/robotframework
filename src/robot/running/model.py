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

from fixture import Setup, Teardown, SuiteSetupListener, SuiteTearDownListener,\
    TestSetupListener, TestTeardownListener
from timeouts import TestTimeout
from keywords import Keywords
from namespace import Namespace
from runerrors import SuiteRunErrors, TestRunErrors
from userkeyword import UserLibrary


def TestSuite(datasources, settings):
    suitedata = TestSuiteData(datasources, settings['SuiteNames'])
    suite = RunnableTestSuite(suitedata)
    suite.set_options(settings)
    return suite


class ExecutionContext(object):

    def __init__(self, namespace, output, dry_run=False):
        self.namespace = namespace
        self.output = output
        self.dry_run = dry_run

    def get_current_vars(self):
        return self.namespace.variables

    def end_test(self, test):
        self.output.end_test(test)
        self.namespace.end_test()

    def end_suite(self, suite):
        self.output.end_suite(suite)
        self.namespace.end_suite()

    def output_file_changed(self, filename):
        self._set_global_variable('${OUTPUT_FILE}', filename)

    def replace_vars_from_setting(self, name, value, errors):
        return self.namespace.variables.replace_meta(name, value, errors)

    def log_file_changed(self, filename):
        self._set_global_variable('${LOG_FILE}', filename)

    def set_prev_test_variables(self, test):
        self._set_prev_test_variables(self.get_current_vars(), test.name,
                                      test.status, test.message)

    def copy_prev_test_vars_to_global(self):
        varz = self.get_current_vars()
        name, status, message = varz['${PREV_TEST_NAME}'], \
                    varz['${PREV_TEST_STATUS}'], varz['${PREV_TEST_MESSAGE}']
        self._set_prev_test_variables(GLOBAL_VARIABLES, name, status, message)

    def _set_prev_test_variables(self, destination, name, status, message):
        destination['${PREV_TEST_NAME}'] = name
        destination['${PREV_TEST_STATUS}'] = status
        destination['${PREV_TEST_MESSAGE}'] = message

    def _set_global_variable(self, name, value):
        self.namespace.variables.set_global(name, value)

    def report_suite_status(self, status, message):
        self.get_current_vars()['${SUITE_STATUS}'] = status
        self.get_current_vars()['${SUITE_MESSAGE}'] = message

    def start_test(self, test):
        self.namespace.start_test(test)
        self.output.start_test(test)

    def set_test_status_before_teardown(self, message, status):
        self.namespace.set_test_status_before_teardown(message, status)

    def get_handler(self, name):
        return self.namespace.get_handler(name)

    def start_keyword(self, keyword):
        self.output.start_keyword(keyword)

    def end_keyword(self, keyword):
        self.output.end_keyword(keyword)

    def warn(self, message):
        self.output.warn(message)

    def trace(self, message):
        self.output.trace(message)


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
        self._run_mode_dry_run = False

    def run(self, output, parent=None, errors=None):
        context = self._start_run(output, parent, errors)
        self._run_setup(context)
        self._run_sub_suites(context)
        self._run_tests(context)
        self._report_status(context)
        self._run_teardown(context)
        self._end_run(context)

    def _start_run(self, output, parent, errors):
        if not errors:
            errors = SuiteRunErrors(self._run_mode_exit_on_failure)
        self.run_errors = errors
        self.run_errors.start_suite()
        self.status = 'RUNNING'
        self.starttime = utils.get_timestamp()
        parent_vars = parent.context.get_current_vars() if parent else None
        self.context = ExecutionContext(Namespace(self, parent_vars), output,
                                        self._run_mode_dry_run)
        self._set_variable_dependent_metadata(self.context)
        output.start_suite(self)
        return self.context

    def _set_variable_dependent_metadata(self, context):
        errors = []
        self.doc = context.replace_vars_from_setting('Documentation', self.doc,
                                                     errors)
        self.setup = Setup(context.replace_vars_from_setting('Setup', self.setup,
                                                             errors))
        self.teardown = Teardown(context.replace_vars_from_setting('Teardown',
                                                                   self.teardown,
                                                                   errors))
        for name, value in self.metadata.items():
            self.metadata[name] = context.replace_vars_from_setting(name, value,
                                                                    errors)
        if errors:
            self.run_errors.suite_init_err('Suite initialization failed:\n%s'
                                            % '\n'.join(errors))

    def _run_setup(self, context):
        if self.run_errors.is_suite_setup_allowed():
            self.setup.run(context, SuiteSetupListener(self))
            self.run_errors.setup_executed()

    def _run_teardown(self, context):
        if self.run_errors.is_suite_teardown_allowed():
            self.teardown.run(context, SuiteTearDownListener(self))

    def _run_sub_suites(self, context):
        for suite in self.suites:
            suite.run(context.output, self, self.run_errors)

    def _run_tests(self, context):
        executed_tests = []
        for test in self.tests:
            normname = utils.normalize(test.name)
            if normname in executed_tests:
                LOGGER.warn("Multiple test cases with name '%s' executed in "
                            "test suite '%s'"% (test.name, self.longname))
            executed_tests.append(normname)
            test.run(context, self.run_errors)
            context.set_prev_test_variables(test)

    def _report_status(self, context):
        self.set_status()
        self.message = self.run_errors.suite_error()
        context.report_suite_status(self.status, self.get_full_message())

    def _end_run(self, context):
        self.endtime = utils.get_timestamp()
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)
        context.copy_prev_test_vars_to_global()
        context.end_suite(self)
        self.run_errors.end_suite()


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
        self.keywords = Keywords(data.keywords)

    def run(self, context, suite_errors):
        self._suite_errors = suite_errors
        self._start_run(context)
        if self.run_errors.is_allowed_to_run():
            self._run(context)
        else:
            self._not_allowed_to_run()
        self._end_run(context)

    def _start_run(self, context):
        self.run_errors = TestRunErrors(self._suite_errors)
        self.status = 'RUNNING'
        self.starttime = utils.get_timestamp()
        self.run_errors.init_err(self._init_test(context))
        context.start_test(self)

    def _init_test(self, context):
        errors = []
        self.doc = context.replace_vars_from_setting('Documentation', self.doc,
                                                     errors)
        self.setup = Setup(context.replace_vars_from_setting('Setup', self.setup,
                                                             errors))
        self.teardown = Teardown(context.replace_vars_from_setting('Teardown',
                                                                   self.teardown,
                                                                   errors))
        self.tags = utils.normalize_tags(context.replace_vars_from_setting('Tags',
                                                                           self.tags,
                                                                           errors))
        self.timeout = TestTimeout(*context.replace_vars_from_setting('Timeout',
                                                                      self.timeout,
                                                                      errors))
        if errors:
            return 'Test case initialization failed:\n%s' % '\n'.join(errors)
        if not self.keywords:
            return 'Test case contains no keywords'
        return None

    def _run(self, context):
        self.timeout.start()
        self._run_setup(context)
        if not self.run_errors.setup_failed():
            try:
                self.keywords.run(context)
            except ExecutionFailed, err:
                self.run_errors.kw_err(unicode(err))
                self.keyword_failed(err)
        context.set_test_status_before_teardown(*self._report_status())
        self._run_teardown(context)
        self._report_status_after_teardown()

    def keyword_failed(self, err):
        self.timeout.set_keyword_timeout(err.timeout)
        self._suite_errors.test_failed(exit=err.exit)

    def _run_setup(self, context):
        self.setup.run(context, TestSetupListener(self))

    def _report_status(self):
        message = self.run_errors.get_message()
        if message:
            self.status = 'FAIL'
            self.message = message
        else:
            self.status = 'PASS'
        return self.message, self.status

    def _run_teardown(self, context):
        self.teardown.run(context, TestTeardownListener(self))

    def _report_status_after_teardown(self):
        if self.run_errors.teardown_failed():
            self.status = 'FAIL'
            self.message = self.run_errors.get_teardown_message(self.message)
        if self.status == 'PASS' and self.timeout.timed_out():
            self.status = 'FAIL'
            self.message = self.timeout.get_message()
        if self.status == 'FAIL':
            self._suite_errors.test_failed(critical=self.critical=='yes')

    def _not_allowed_to_run(self):
        self.status = 'FAIL'
        self.message = self.run_errors.parent_or_init_error()

    def _end_run(self, context):
        self.endtime = utils.get_timestamp()
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)
        context.end_test(self)


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
