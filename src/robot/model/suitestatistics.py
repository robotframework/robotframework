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

from robot.model.stats import SuiteStat


class SuiteStatistics(object):

    def __init__(self, suite):
        self.all = SuiteStat(suite)
        self.critical = SuiteStat(suite)
        self.suites = []

    def add_test(self, test):
        self.all.add_test(test)
        if test.critical == 'yes':
            self.critical.add_test(test)

    def visit(self, visitor):
        visitor.visit_suite_statistics(self)

    def __iter__(self):
        yield self.all
        for s in self.suites:
            for stat in s:
                yield stat
