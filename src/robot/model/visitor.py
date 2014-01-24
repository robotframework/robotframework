#  Copyright 2008-2014 Nokia Solutions and Networks
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

class SuiteVisitor(object):

    def visit_suite(self, suite):
        if self.start_suite(suite) is not False:
            suite.keywords.visit(self)
            suite.suites.visit(self)
            suite.tests.visit(self)
            self.end_suite(suite)

    def start_suite(self, suite):
        pass

    def end_suite(self, suite):
        pass

    def visit_test(self, test):
        if self.start_test(test) is not False:
            test.keywords.visit(self)
            self.end_test(test)

    def start_test(self, test):
        pass

    def end_test(self, test):
        pass

    def visit_keyword(self, kw):
        if self.start_keyword(kw) is not False:
            kw.keywords.visit(self)
            kw.messages.visit(self)
            self.end_keyword(kw)

    def start_keyword(self, keyword):
        pass

    def end_keyword(self, keyword):
        pass

    def visit_message(self, msg):
        if self.start_message(msg) is not False:
            self.end_message(msg)

    def start_message(self, msg):
        pass

    def end_message(self, msg):
        pass


class SkipAllVisitor(SuiteVisitor):
    """Travels suite and it's sub-suites without doing anything."""
    def visit_suite(self, suite):
        pass

    def visit_keyword(self, kw):
        pass

    def visit_test(self, test):
        pass

    def visit_message(self, msg):
        pass
