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

from robot import utils
from robot.common import BaseTestSuite, BaseTestCase
from robot.parsing import TestData
from robot.errors import ExecutionFailed, DataError
from robot.variables import GLOBAL_VARIABLES
from robot.output import LOGGER

from .fixture import Setup, Teardown
from .keywords import Keywords
from .namespace import Namespace
from .runerrors import SuiteRunErrors, TestRunErrors
from .userkeyword import UserLibrary
from .context import EXECUTION_CONTEXTS
from .defaultvalues import DefaultValues


def TestSuite(datasources, settings, process_variables=True):
    """Creates a runnable test suite from given data sources and settings.

    This is a factory method that returns either :class:`RunnableTestSuite`
    or :class:`RunnableMultiTestSuite` depending are one or more data sources
    given. This method, and especially the returned suite, is likely to change
    heavily in version 2.8.

    :param datasources: List of paths to read data from. Starting from 2.7.2,
                        a single datasource can also be given as a string.
    :param settings: Execution configuration.
    :type settings: :class:`~robot.conf.settings.RobotSettings`
    :returns: :class:`RunnableTestSuite`
    """
    if isinstance(datasources, basestring):
        datasources = [datasources]
    datasources = [utils.abspath(path) for path in datasources]
    suite = _get_suite(datasources, settings['SuiteNames'],
                       settings['WarnOnSkipped'], process_variables)
    suite.set_options(settings)
    _check_suite_contains_tests(suite, settings['RunEmptySuite'])
    return suite

def _get_suite(sources, include_suites, warn_on_skipped, process_variables):
    if not sources:
        raise DataError("No data sources given.")
    if len(sources) > 1:
        return _get_multisource_suite(sources, include_suites,
                                      warn_on_skipped, process_variables)
    data = _parse_suite(sources[0], include_suites, warn_on_skipped)
    return RunnableTestSuite(data, process_variables=process_variables)

def _parse_suite(path, include_suites, warn_on_skipped):
    try:
        return TestData(source=path, include_suites=include_suites,
                        warn_on_skipped=warn_on_skipped)
    except DataError, err:
        raise DataError("Parsing '%s' failed: %s" % (path, unicode(err)))

def _get_multisource_suite(sources, include_suites, warn_on_skipped, process_variables):
    data = []
    for src in sources:
        try:
            data.append(_parse_suite(src, include_suites, warn_on_skipped))
        except DataError, err:
            LOGGER.warn(err)
    suite = RunnableMultiTestSuite(data, process_variables)
    if suite.get_test_count() == 0:
        raise DataError("Data sources %s contain no test cases." % utils.seq2str(sources))
    return suite

def _check_suite_contains_tests(suite, run_empty_suites=False):
    suite.filter_empty_suites()
    if not suite.get_test_count() and not run_empty_suites:
        raise DataError("Test suite '%s' contains no test cases." % suite.source)


class RunnableTestSuite(BaseTestSuite):

    def __init__(self, data, parent=None, defaults=None, process_variables=True):
        BaseTestSuite.__init__(self, data.name, data.source, parent)
        self.variables = GLOBAL_VARIABLES.copy()
        if process_variables:
            self.variables.set_from_variable_table(data.variable_table)
        self.source = data.source
        self.doc = data.setting_table.doc.value
        self.metadata = self._get_metadata(data.setting_table.metadata)
        self.imports = data.imports
        self.user_keywords = UserLibrary(data.keywords)
        self.setup = Setup(data.setting_table.suite_setup.name,
                           data.setting_table.suite_setup.args)
        self.teardown = Teardown(data.setting_table.suite_teardown.name,
                                 data.setting_table.suite_teardown.args)
        defaults = DefaultValues(data.setting_table, defaults)
        for suite in data.children:
            RunnableTestSuite(suite, self, defaults, process_variables)
        for test in data.testcase_table:
            RunnableTestCase(test, self, defaults)
        self._exit_on_failure_mode = False
        self._skip_teardowns_on_exit_mode = False
        self._dry_run_mode = False

    def filter_empty_suites(self):
        for suite in self.suites[:]:
            suite.filter_empty_suites()
            if suite.get_test_count() == 0:
                self.suites.remove(suite)
                LOGGER.info("Running test suite '%s' failed: Test suite "
                            "contains no test cases." % suite.source)

    def _get_metadata(self, metadata):
        meta = utils.NormalizedDict()
        for item in metadata:
            meta[item.name] = item.value
        return meta

    def run(self, output, parent_context=None, errors=None):
        if not errors:
            errors = SuiteRunErrors(self._exit_on_failure_mode,
                                    self._skip_teardowns_on_exit_mode)
        context = self._start_run(output, parent_context, errors)
        self._run_setup(context, errors)
        self._run_sub_suites(context, errors)
        self._run_tests(context, errors)
        self._report_status(context, errors)
        self._run_teardown(context, errors)
        self._end_run(context, errors)

    def _start_run(self, output, parent_context, errors):
        errors.start_suite()
        self.status = 'RUNNING'
        self.starttime = utils.get_timestamp()
        variables = parent_context.get_current_vars() if parent_context else None
        ns = Namespace(self, variables)
        context = EXECUTION_CONTEXTS.start_suite(ns, output, self._dry_run_mode)
        if not errors.exit:
            ns.handle_imports()
        self.variables.resolve_delayed()
        self._set_variable_dependent_metadata(context, errors)
        output.start_suite(self)
        return context

    def _set_variable_dependent_metadata(self, context, errors):
        init_errors = []
        self.doc = context.replace_vars_from_setting('Documentation', self.doc,
                                                     init_errors)
        self.setup.replace_variables(context.get_current_vars(), init_errors)
        self.teardown.replace_variables(context.get_current_vars(), init_errors)
        for name, value in self.metadata.items():
            self.metadata[name] = context.replace_vars_from_setting(name, value,
                                                                    init_errors)
        errors.suite_initialized('\n'.join(init_errors))

    def _run_setup(self, context, errors):
        if errors.is_setup_allowed():
            error = self.setup.run(context)
            errors.setup_executed(error)

    def _run_teardown(self, context, errors):
        if errors.is_teardown_allowed():
            error = self.teardown.run(context)
            if error:
                self.suite_teardown_failed(error)

    def _run_sub_suites(self, context, errors):
        for suite in self.suites:
            suite.run(context.output, context, errors)

    def _run_tests(self, context, errors):
        executed_tests = []
        for test in self.tests:
            normname = utils.normalize(test.name)
            if normname in executed_tests:
                LOGGER.warn("Multiple test cases with name '%s' executed in "
                            "test suite '%s'"% (test.name, self.longname))
            executed_tests.append(normname)
            test.run(context, errors)
            context.set_prev_test_variables(test)

    def _report_status(self, context, errors):
        self.set_status()
        self.message = errors.get_suite_error()
        context.report_suite_status(self.status, self.get_full_message())

    def _end_run(self, context, errors):
        self.endtime = utils.get_timestamp()
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)
        context.copy_prev_test_vars_to_global()
        context.end_suite(self)
        errors.end_suite()


class RunnableMultiTestSuite(RunnableTestSuite):

    def __init__(self, suitedatas, process_variables=True):
        BaseTestSuite.__init__(self, name='')
        self.variables = GLOBAL_VARIABLES.copy()
        self.doc = ''
        self.imports = []
        self.setup = Setup(None, None)
        self.teardown = Teardown(None, None)
        for suite in suitedatas:
            RunnableTestSuite(suite, self, process_variables=process_variables)
        self._exit_on_failure_mode = False
        self._skip_teardowns_on_exit_mode = False
        self._dry_run_mode = False


class RunnableTestCase(BaseTestCase):

    def __init__(self, tc_data, parent, defaults):
        BaseTestCase.__init__(self, tc_data.name, parent)
        self.doc = tc_data.doc.value
        self.setup = defaults.get_setup(tc_data.setup)
        self.teardown = defaults.get_teardown(tc_data.teardown)
        self.tags = defaults.get_tags(tc_data.tags)
        self.timeout = defaults.get_timeout(tc_data.timeout)
        self._template = defaults.get_template(tc_data.template)
        self._steps = tc_data.steps
        self._keywords = None

    def run(self, context, parent_errors):
        errors = self._start_run(context, parent_errors)
        if errors.is_run_allowed():
            self._run(context, errors)
        else:
            self._not_allowed_to_run(errors)
        self._end_run(context)

    @property
    def keywords(self):
        if self._keywords is None:
            self._keywords = Keywords(self._steps, self.template)
        return self._keywords

    @property
    def template(self):
        return self._template.name

    def _start_run(self, context, parent_errors):
        errors = TestRunErrors(parent_errors)
        self.status = 'RUNNING'
        self.starttime = utils.get_timestamp()
        errors.test_initialized(self._init_test(context))
        context.start_test(self)
        return errors

    def _init_test(self, context):
        errors = []
        self.doc = context.replace_vars_from_setting('Documentation', self.doc,
                                                     errors)
        self.setup.replace_variables(context.get_current_vars(), errors)
        self.teardown.replace_variables(context.get_current_vars(), errors)
        self._template.replace_variables(context.get_current_vars(), errors)
        self._keywords = None
        tags = context.replace_vars_from_setting('Tags', self.tags, errors)
        self.tags = utils.normalize_tags(tags)
        self.timeout.replace_variables(context.get_current_vars())
        if errors:
            return 'Test case initialization failed:\n%s' % '\n'.join(errors)
        if not self.name:
            return 'Test case name is required.'
        if not self.keywords:
            return 'Test case contains no keywords'
        return None

    def _run(self, context, errors):
        self.timeout.start()
        failed = self._run_setup(context, errors)
        if not failed:
            self._run_keywords(context, errors)
        self._set_status_before_teardown(context, errors)
        failed = self._run_teardown(context, errors)
        self._set_status_after_teardown(failed, errors)

    def _test_failed(self, err, errors):
        self.timeout.set_keyword_timeout(err.timeout)
        errors.test_failed(exit=err.exit, critical=self.critical)

    def _run_setup(self, context, errors):
        error = self.setup.run(context)
        if error:
            errors.setup_failed(error)
            self._test_failed(error, errors)
        return bool(error)

    def _run_keywords(self, context, errors):
        try:
            self.keywords.run(context)
        except ExecutionFailed, err:
            errors.keyword_failed(err)
            self._test_failed(err, errors)

    def _set_status_before_teardown(self, context, errors):
        message = errors.get_message()
        if message:
            self.status = 'FAIL'
            self.message = message
        else:
            self.status = 'PASS'
        context.set_test_status_before_teardown(self.message, self.status)

    def _run_teardown(self, context, errors):
        if not errors.is_teardown_allowed():
            return False
        error = self.teardown.run(context)
        if error:
            errors.teardown_failed(error)
            self._test_failed(error, errors)
        return bool(error)

    def _set_status_after_teardown(self, teardown_failed, errors):
        if teardown_failed:
            self.status = 'FAIL'
            self.message = errors.get_teardown_message(self.message)
        if self.status == 'PASS' and self.timeout.timed_out():
            self.status = 'FAIL'
            self.message = self.timeout.get_message()
        if self.status == 'FAIL':
            errors.test_failed(critical=self.critical)

    def _not_allowed_to_run(self, errors):
        self.status = 'FAIL'
        self.message = errors.get_parent_or_init_error()

    def _end_run(self, context):
        self.endtime = utils.get_timestamp()
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)
        context.end_test(self)
