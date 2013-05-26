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

from robot.model import SuiteVisitor
from robot.result.testsuite import TestSuite     # TODO: expose in __init__?
from robot.result.executionresult import Result  # ---------- ii -----------
from robot.running.namespace import Namespace
from robot.variables import GLOBAL_VARIABLES
from robot.running.context import EXECUTION_CONTEXTS
from robot.running.keywords import Keywords, Keyword
from robot.running.userkeyword import UserLibrary
from robot.errors import ExecutionFailed, DataError
from robot import utils

from .failures import ExecutionStatus


class Runner(SuiteVisitor):

    def __init__(self, output):
        self.result = None
        self._output = output
        self._suite = None
        self._suite_status = None

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
        EXECUTION_CONTEXTS.start_suite(ns, self._output, False)
        ns.handle_imports()
        variables.resolve_delayed()
        result = TestSuite(name=suite.name,
                           doc=self._resolve_setting(suite.doc),
                           metadata=suite.metadata,
                           source=suite.source,
                           starttime=utils.get_timestamp())
        if not self.result:
            self.result = Result(root_suite=result)
        else:
            self._suite.suites.append(result)
        self._suite_status = ExecutionStatus(self._suite_status)
        self._suite = result
        self._output.start_suite(self._suite)
        self._run_setup(suite.keywords.setup, self._suite_status)

    def _resolve_setting(self, value):
        value = self._variables.replace_string(value, ignore_errors=True)
        return utils.unescape(value)

    def end_suite(self, suite):
        failure = self._run_teardown(suite.keywords.teardown, self._suite_status)
        if failure:
            self._suite.suite_teardown_failed(unicode(failure))
        self._suite.endtime = utils.get_timestamp()
        self._suite.message = self._suite_status.message
        self._context.end_suite(self._suite)
        self._suite = self._suite.parent
        self._suite_status = self._suite_status.parent_status

    def visit_test(self, test):
        result = self._suite.tests.create(name=test.name,
                                          doc=self._resolve_setting(test.doc),
                                          tags=test.tags,
                                          starttime=utils.get_timestamp())
        keywords = Keywords(test.keywords.normal, test.continue_on_failure)
        result.timeout = test.timeout   # TODO: Cleaner implementation to ...
        result.status = 'RUNNING'       # ... activate timeouts
        self._context.start_test(result)
        if test.timeout:
            test.timeout.replace_variables(self._variables)  # FIXME: Should not change model state!!
            test.timeout.start()
        status = ExecutionStatus(self._suite_status, test=True)
        if not status.failures:
            self._run_setup(test.keywords.setup, status)
        try:
            if not status.failures:
                keywords.run(self._context)
        except ExecutionFailed, err:
            status.test_failed(err)
        result.status = status.status
        result.message = status.message
        if status.teardown_allowed:
            self._run_teardown(test.keywords.teardown, status)
        result.status = status.status
        result.message = status.message
        result.endtime = utils.get_timestamp()
        self._context.end_test(result)

    def _run_setup(self, setup, failures):
        failure = self._run_setup_or_teardown(setup, 'setup')
        failures.setup_executed(failure)

    def _run_teardown(self, teardown, failures):
        failure = self._run_setup_or_teardown(teardown, 'teardown')
        failures.teardown_executed(failure)
        return failure

    def _run_setup_or_teardown(self, data, type):
        if not data:
            return None
        try:
            name = self._variables.replace_string(data.name)
        except DataError, err:
            return err
        if name.upper() == 'NONE':
            return None
        kw = Keyword(name, data.args, type=type)
        try:
            kw.run(self._context)
        except ExecutionFailed, err:
            return err
