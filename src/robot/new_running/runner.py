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
from robot.running.context import EXECUTION_CONTEXTS
from robot.running.keywords import Keyword, Keywords
from robot.errors import ExecutionFailed


class Runner(SuiteVisitor):

    def __init__(self, output):
        self.output = output
        self.result = None
        self.current = None

    def start_suite(self, suite):
        if not self.result:
            self.result = TestSuite(name=suite.name)
            self.current = self.result
        ns = Namespace(suite, None)
        ns.handle_imports()
        self.context = EXECUTION_CONTEXTS.start_suite(ns, self.output, False)

    def visit_test(self, test):
        result = self.result.tests.create(name=test.name)
        keywords = Keywords(test.keywords)
        try:
            keywords.run(self.context)
        except ExecutionFailed, err:
            result.message = unicode(err)
            result.status = 'FAIL'
        else:
            result.status = 'PASS'
