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

from __future__ import with_statement

from robot.model import SuiteVisitor
from robot.result.testsuite import TestSuite     # TODO: expose in __init__?
from robot.result.executionresult import Result  # ---------- ii -----------
from robot.running.namespace import Namespace
from robot.running.timeouts import TestTimeout
from robot.variables import GLOBAL_VARIABLES
from robot.running.context import EXECUTION_CONTEXTS
from robot.running.keywords import Keywords, Keyword
from robot.running.userkeyword import UserLibrary
from robot.errors import ExecutionFailed, DataError
from robot import utils

from .status import SuiteStatus, TestStatus


class Runner(SuiteVisitor):

    def __init__(self, output, settings):
        self.result = None
        self._output = output
        self._settings = settings
        self._suite = None
        self._suite_status = None
        self._executed_tests = None

    @property
    def _context(self):
        return EXECUTION_CONTEXTS.current

    @property
    def _variables(self):
        return self._context.namespace.variables

    def start_suite(self, suite):
        variables = GLOBAL_VARIABLES.copy()
        variables.set_from_variable_table(suite.variables)
        ns = Namespace(suite,
                       self._context.namespace.variables if self._context else None,
                       UserLibrary(suite.user_keywords),
                       variables)
        EXECUTION_CONTEXTS.start_suite(ns, self._output, self._settings.dry_run)
        if not (self._suite_status and self._suite_status.failures):  # Skips imports if exiting
            ns.handle_imports()
        variables.resolve_delayed()
        result = TestSuite(name=suite.name,
                           doc=self._resolve_setting(suite.doc),
                           metadata=[(self._resolve_setting(n),
                                      self._resolve_setting(v))
                                     for n, v in suite.metadata.items()],
                           source=suite.source,
                           starttime=utils.get_timestamp())
        if not self.result:
            result.set_criticality(suite.criticality.critical_tags,
                                   suite.criticality.non_critical_tags)
            self.result = Result(root_suite=result)
        else:
            self._suite.suites.append(result)
        self._suite = result
        self._suite_status = SuiteStatus(self._suite_status,
                                         self._settings.exit_on_failure,
                                         self._settings.skip_teardown_on_exit)
        self._output.start_suite(self._suite)
        self._run_setup(suite.keywords.setup, self._suite_status)
        self._executed_tests = utils.NormalizedDict(ignore='_')

    def _resolve_setting(self, value):
        return self._variables.replace_string(value, ignore_errors=True)

    def end_suite(self, suite):
        self._suite.message = self._suite_status.message
        self._context.report_suite_status(self._suite.status,
                                          self._suite.full_message)
        with self._context.in_suite_teardown:
            failure = self._run_teardown(suite.keywords.teardown, self._suite_status)
            if failure:
                self._suite.suite_teardown_failed(unicode(failure))
        self._suite.endtime = utils.get_timestamp()
        self._suite.message = self._suite_status.message
        self._context.end_suite(self._suite)
        self._suite = self._suite.parent
        self._suite_status = self._suite_status.parent

    def visit_test(self, test):
        if test.name in self._executed_tests:
            self._output.warn("Multiple test cases with name '%s' executed in "
                              "test suite '%s'." % (test.name, self._suite.longname))
        self._executed_tests[test.name] = True
        result = self._suite.tests.create(name=test.name,
                                          doc=self._resolve_setting(test.doc),
                                          tags=[self._resolve_setting(t)
                                                for t in test.tags],
                                          starttime=utils.get_timestamp(),
                                          timeout=self._get_timeout(test),
                                          status='RUNNING')
        keywords = Keywords(test.keywords.normal, test.continue_on_failure)
        self._context.start_test(result)
        status = TestStatus(self._suite_status)
        if not test.name:
            status.test_failed('Test case name cannot be empty.', test.critical)
        if not keywords:
            status.test_failed('Test case contains no keywords.', test.critical)
        self._run_setup(test.keywords.setup, status)
        try:
            if not status.failures:
                keywords.run(self._context)
        except ExecutionFailed, err:
            status.test_failed(err, test.critical)
        result.status = status.status
        result.message = status.message or result.message
        if status.teardown_allowed:
            self._context.set_test_status_before_teardown(status.message, status.status)  # TODO: This is fugly
            self._run_teardown(test.keywords.teardown, status)
        result.status = status.status
        result.message = status.message or result.message
        result.endtime = utils.get_timestamp()
        self._context.end_test(result)

    def _get_timeout(self, test):
        if not test.timeout:
            return None
        timeout = TestTimeout(test.timeout.value, test.timeout.message,
                              self._variables)
        timeout.start()
        return timeout

    def _run_setup(self, setup, status):
        if not status.failures:
            failure = self._run_setup_or_teardown(setup, 'setup')
            status.setup_executed(failure)

    def _run_teardown(self, teardown, status):
        if status.teardown_allowed:
            failure = self._run_setup_or_teardown(teardown, 'teardown')
            status.teardown_executed(failure)
            return failure

    def _run_setup_or_teardown(self, data, type):
        if not data:
            return None
        try:
            name = self._variables.replace_string(data.name)
        except DataError, err:
            return err
        if name.upper() in ('', 'NONE'):
            return None
        kw = Keyword(name, data.args, type=type)
        try:
            kw.run(self._context)
        except ExecutionFailed, err:
            return err
