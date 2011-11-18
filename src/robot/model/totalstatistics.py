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

from robot.model.stats import TotalStat


class TotalStatistics(object):

    def __init__(self):
        self.critical = TotalStat('Critical Tests')
        self.all = TotalStat('All Tests')

    def visit(self, visitor):
        visitor.visit_total_statistics(self)

    def __iter__(self):
        return iter([self.critical, self.all])


class TotalStatisticsBuilder(object):

    def __init__(self):
        self.stats = TotalStatistics()

    def add_test(self, test):
        self.stats.all.add_test(test)
        if test.critical == 'yes':
            self.stats.critical.add_test(test)
