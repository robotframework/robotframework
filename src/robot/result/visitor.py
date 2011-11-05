#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

    def visit_suite(self, suite):
        pass

    def visit_keyword(self, kw):
        pass

    def visit_test(self, test):
        pass

    def visit_message(self, msg):
        pass


class ResultVisitor(SuiteVisitor):

    def visit_result(self, result):
        self.start_result(result)
        self.visit_suite(result.suite)
        self.visit_statistics(result.statistics)
        self.visit_errors(result.errors)
        self.end_result(result)

    def start_result(self, result):
        pass

    def end_result(self, result):
        pass

    def visit_statistics(self, stats):
        # TODO: Fix once statistics are rewritten
        self.start_statistics(stats)
        stats.total.serialize(self)
        stats.tags.serialize(self)
        stats.suite.serialize(self)
        self.end_statistics(stats)

    def start_statistics(self, stats):
        pass

    def start_total_stats(self, total_stats):
        pass

    def total_stat(self, total_stat):
        pass

    def end_total_stats(self, total_stats):
        pass

    def start_tag_stats(self, tag_stats):
        pass

    def tag_stat(self, tag_stat):
        pass

    def end_tag_stats(self, tag_stats):
        pass

    def start_suite_stats(self, suite_stats):
        pass

    def suite_stat(self, suite_stat):
        pass

    def end_suite_stats(self, suite_stats):
        pass

    def end_statistics(self, stats):
        pass

    def visit_errors(self, errors):
        self.start_errors(errors)
        for msg in errors.messages: # TODO: should errors itself be iterable?
            self.visit_message(msg)
        self.end_errors(errors)

    def start_errors(self, errors):
        pass

    def end_errors(self, errors):
        pass
