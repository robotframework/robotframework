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
from robot.running.keywords import Keywords
from robot.running.fixture import Setup, Teardown
from robot.running.userkeyword import UserLibrary
from robot.errors import ExecutionFailed
from robot import utils


class Runner(SuiteVisitor):

    def __init__(self, output):
        self.result = None
        self._output = output
        self._suite = None

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
        self._suite = result
        self._output.start_suite(self._suite)
        self._setup(suite.keywords.setup).run(self._context)

    def _resolve_setting(self, value):
        value = self._variables.replace_string(value, ignore_errors=True)
        return utils.unescape(value)

    def end_suite(self, suite):
        self._teardown(suite.keywords.teardown).run(self._context)
        self._suite.endtime = utils.get_timestamp()
        self._context.end_suite(self._suite)
        self._suite = self._suite.parent

    def visit_test(self, test):
        result = self._suite.tests.create(name=test.name,
                                          doc=self._resolve_setting(test.doc),
                                          tags=test.tags,
                                          starttime=utils.get_timestamp())
        setup = self._setup(test.keywords.setup)
        keywords = Keywords(test.keywords.normal)
        teardown = self._teardown(test.keywords.teardown)
        result.timeout = test.timeout   # TODO: Cleaner implementation to ...
        result.status = 'RUNNING'       # ... activate timeouts
        self._context.start_test(result)
        if test.timeout:
            test.timeout.replace_variables(self._variables)  # FIXME: Should not change model state!!
            test.timeout.start()
        setup.run(self._context)
        try:
            keywords.run(self._context)
        except ExecutionFailed, err:
            result.message = unicode(err)
            result.status = 'FAIL'
        else:
            result.status = 'PASS'
        teardown.run(self._context)
        result.endtime = utils.get_timestamp()
        self._context.end_test(result)

    def _setup(self, setup):
        if not setup:
            return Setup('', ())
        setup = Setup(setup.name, setup.args)
        setup.replace_variables(self._variables, [])
        return setup

    def _teardown(self, teardown):
        if not teardown:
            return Teardown('', ())
        teardown = Teardown(teardown.name, teardown.args)
        teardown.replace_variables(self._variables, [])
        return teardown
