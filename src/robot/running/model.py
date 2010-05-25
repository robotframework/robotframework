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

import os

from robot import utils
from robot.common import BaseTestSuite, BaseTestCase
from robot.parsing import TestCaseFile, TestDataDirectory
from robot.parsing.settings import Fixture
from robot.errors import ExecutionFailed, DataError
from robot.variables import GLOBAL_VARIABLES
from robot.output import LOGGER

from fixture import Setup, Teardown, SuiteSetupListener, SuiteTearDownListener,\
    TestSetupListener, TestTeardownListener
from timeouts import TestTimeout
from keywords import Keywords
from namespace import Namespace
from runerrors import SuiteRunErrors, TestRunErrors
from userkeyword import UserLibrary
from context import ExecutionContext


def TestSuite(datasources, settings):
    datasources = [ utils.normpath(path) for path in datasources ]
    include_suites = settings['SuiteNames']
    if not datasources:
        raise DataError("No data sources given.")
    elif len(datasources) > 1:
        suitedatas = []
        for datasource in datasources:
            try:
                suitedatas.append(_get_directory_or_file_suite(datasource, 
                                                               include_suites))
            except DataError:
                pass
        suite = RunnableMultiTestSuite(suitedatas)
    else:
        suitedata = _get_directory_or_file_suite(datasources[0], include_suites)
        suite = RunnableTestSuite(suitedata)
    suite.set_options(settings)
    return suite

def _get_directory_or_file_suite(path, include_suites):
    if os.path.isdir(path):
        return TestDataDirectory(source=path, include_suites=include_suites)
    return TestCaseFile(source=path)


class RunnableTestSuite(BaseTestSuite):

    def __init__(self, data, parent=None):
        BaseTestSuite.__init__(self, data.name, data.source, parent)
        self.variables = GLOBAL_VARIABLES.copy()
        self.variables.set_from_variable_table(data.variable_table)
        self.source = data.source
        self.doc = data.setting_table.doc.value
        self.metadata = self._get_metadata(data.setting_table.metadata)
        self.imports = data.setting_table.imports
        self.user_keywords = UserLibrary(data.keyword_table.keywords)
        self.setup = Setup(data.setting_table.suite_setup.name, 
                           data.setting_table.suite_setup.args)
        self.teardown = Teardown(data.setting_table.suite_teardown.name, 
                                 data.setting_table.suite_teardown.args)
        for suite in data.children:
            RunnableTestSuite(suite, parent=self)
        for test in data.testcase_table:
            RunnableTestCase(test, parent=self)
        self._run_mode_exit_on_failure = False
        self._run_mode_dry_run = False


    def _get_metadata(self, metadata):
        meta = {}
        for item in metadata:
            meta[item.name] = item.value
        return meta

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
        self.setup.replace_variables(context.get_current_vars())
        self.teardown.replace_variables(context.get_current_vars())
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


class RunnableMultiTestSuite(RunnableTestSuite):

    def __init__(self, suitedatas):
        BaseTestSuite.__init__(self, name='')
        self.variables = GLOBAL_VARIABLES.copy()
        self.doc = ''
        self.imports = []
        # FIXME: remove if possible
        #self.user_keywords = UserLibrary(data.keyword_table.keywords)
        self.setup = Setup(None, None)
        self.teardown = Teardown(None, None)
        for suite in suitedatas:
            RunnableTestSuite(suite, parent=self)
        self._run_mode_exit_on_failure = False
        self._run_mode_dry_run = False


class RunnableTestCase(BaseTestCase):

    def __init__(self, tc_data, parent):
        BaseTestCase.__init__(self, tc_data.name, parent)
        self.doc = tc_data.doc.value
        setup = tc_data.setup.is_set() and tc_data.setup or self._get_parent_test_setup(tc_data.parent.parent)
        self.setup = Setup(setup.name, setup.args)
        teardown = tc_data.teardown.is_set() and tc_data.teardown or self._get_parent_test_teardown(tc_data.parent.parent)
        self.teardown = Teardown(teardown.name, teardown.args)
        self.tags = self._get_tags(tc_data)
        self.timeout = self._get_timeout(tc_data)
        self.keywords = Keywords(tc_data.steps)

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
        self.setup.replace_variables(context.get_current_vars())
        self.teardown.replace_variables(context.get_current_vars())
        self.tags = utils.normalize_tags(context.replace_vars_from_setting('Tags',
                                                                           self.tags,
                                                                           errors))
        self.timeout.replace_variables(context.get_current_vars())
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

    # FIXME: Clean up getting test settings (e.g. Serious Law of Demeter breaking)
    def _get_tags(self, tc_data):
        force_tags = self._get_parent_force_tags(tc_data.parent.parent)
        tc_tags = tc_data.tags.value if tc_data.tags.is_set() \
            else tc_data.parent.parent.setting_table.default_tags.value
        return tc_tags + force_tags

    def _get_parent_force_tags(self, data):
        parent_tags = data.parent and self._get_parent_force_tags(data.parent) or []
        return data.setting_table.force_tags.value + parent_tags

    def _get_parent_test_setup(self, data):
        if data.setting_table.test_setup.is_set():
            return data.setting_table.test_setup
        return data.parent and self._get_parent_test_setup(data.parent) or Fixture()
   
    def _get_parent_test_teardown(self, data):
        if data.setting_table.test_teardown.is_set():
            return data.setting_table.test_teardown
        return data.parent and self._get_parent_test_teardown(data.parent) or Fixture()

    def _get_timeout(self, tc_data):
        if tc_data.timeout.is_set():
            return self._build_timeout(tc_data.timeout)
        return self._build_timeout(tc_data.parent.parent.setting_table.test_timeout)

    def _build_timeout(self, timeout):
        return TestTimeout(timeout.value, timeout.message)

