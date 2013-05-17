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
from robot.result.testsuite import TestSuite # TODO: expose in __init__
from robot.running.namespace import Namespace
from robot.variables import Variables
from robot.running.context import EXECUTION_CONTEXTS
from robot.running.keywords import Keywords
from robot.running.userkeyword import UserLibrary
from robot.errors import ExecutionFailed
from robot import utils


class Runner(SuiteVisitor):

    def __init__(self, output):
        self.output = output
        self.result = None
        self.current = None

    def start_suite(self, suite):
        result = TestSuite(name=suite.name,
                           doc=suite.doc,
                           metadata=suite.metadata,
                           source=suite.source,
                           starttime=utils.get_timestamp())
        if not self.result:
            self.result = self.current = result
        else:
            self.current = self.current.suites.append(suite)
        vars = Variables()
        for var in suite.variables:
            vars[var.name] = var.value
        ns = Namespace(suite, None, UserLibrary(suite.user_keywords), vars)
        self.context = EXECUTION_CONTEXTS.start_suite(ns, self.output, False)
        self.output.start_suite(self.current)
        ns.handle_imports()

    def end_suite(self, suite):
        self.current.endtime = utils.get_timestamp()
        self.context.end_suite(self.current)
        self.current = self.current.parent

    def visit_test(self, test):
        result = self.current.tests.create(name=test.name,
                                           doc=test.doc,
                                           tags=test.tags,
                                           starttime=utils.get_timestamp())
        keywords = Keywords(test.keywords.normal)
        self.context.start_test(result)
        try:
            keywords.run(self.context)
        except ExecutionFailed, err:
            result.message = unicode(err)
            result.status = 'FAIL'
        else:
            result.status = 'PASS'
        result.endtime = utils.get_timestamp()
        self.context.end_test(result)
