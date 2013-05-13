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


class ResultVisitor(SuiteVisitor):

    def visit_result(self, result):
        if self.start_result(result) is not False:
            result.suite.visit(self)
            result.statistics.visit(self)
            result.errors.visit(self)
            self.end_result(result)

    def start_result(self, result):
        pass

    def end_result(self, result):
        pass

    def visit_statistics(self, stats):
        if self.start_statistics(stats) is not False:
            stats.total.visit(self)
            stats.tags.visit(self)
            stats.suite.visit(self)
            self.end_statistics(stats)

    def start_statistics(self, stats):
        pass

    def end_statistics(self, stats):
        pass

    def visit_total_statistics(self, stats):
        if self.start_total_statistics(stats) is not False:
            for stat in stats:
                stat.visit(self)
            self.end_total_statistics(stats)

    def start_total_statistics(self, stats):
        pass

    def end_total_statistics(self, stats):
        pass

    def visit_tag_statistics(self, stats):
        if self.start_tag_statistics(stats) is not False:
            for stat in stats:
                stat.visit(self)
            self.end_tag_statistics(stats)

    def start_tag_statistics(self, stats):
        pass

    def end_tag_statistics(self, stats):
        pass

    def visit_suite_statistics(self, stats):
        if self.start_suite_statistics(stats) is not False:
            for stat in stats:
                stat.visit(self)
            self.end_suite_statistics(stats)

    def start_suite_statistics(self, stats):
        pass

    def end_suite_statistics(self, suite_stats):
        pass

    def visit_stat(self, stat):
        if self.start_stat(stat) is not False:
            self.end_stat(stat)

    def start_stat(self, stat):
        pass

    def end_stat(self, stat):
        pass

    def visit_errors(self, errors):
        self.start_errors(errors)
        for msg in errors:
            msg.visit(self)
        self.end_errors(errors)

    def start_errors(self, errors):
        pass

    def end_errors(self, errors):
        pass
