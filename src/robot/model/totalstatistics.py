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

from .stats import TotalStat
from .visitor import SuiteVisitor


class TotalStatistics(object):

    def __init__(self):
        self.critical = TotalStat('Critical Tests')
        self.all = TotalStat('All Tests')

    def visit(self, visitor):
        visitor.visit_total_statistics(self)

    def __iter__(self):
        return iter([self.critical, self.all])

    @property
    def message(self):
        ctotal, cend, cpass, cfail = self._get_counts(self.critical)
        atotal, aend, apass, afail = self._get_counts(self.all)
        return ('%d critical test%s, %d passed, %d failed\n'
                '%d test%s total, %d passed, %d failed'
                % (ctotal, cend, cpass, cfail, atotal, aend, apass, afail))

    def _get_counts(self, stat):
        ending = 's' if stat.total != 1 else ''
        return stat.total, ending, stat.passed, stat.failed


class TotalStatisticsBuilder(SuiteVisitor):

    def __init__(self, suite=None):
        self.stats = TotalStatistics()
        if suite:
            suite.visit(self)

    def add_test(self, test):
        self.stats.all.add_test(test)
        if test.critical:
            self.stats.critical.add_test(test)

    def visit_test(self, test):
        self.add_test(test)

    def visit_keyword(self, kw):
        pass
