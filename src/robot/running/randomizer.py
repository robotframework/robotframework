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

import random

from robot.model import SuiteVisitor


class Randomizer(SuiteVisitor):

    def __init__(self, randomize_suites=True, randomize_tests=True):
        self.randomize_suites = randomize_suites
        self.randomize_tests = randomize_tests

    def start_suite(self, suite):
        if not self.randomize_suites and not self.randomize_tests:
            return False
        if self.randomize_suites:
            suite.suites = self._shuffle(suite.suites)
        if self.randomize_tests:
            suite.tests = self._shuffle(suite.tests)

    def _shuffle(self, item_list):
        items = list(item_list)
        random.shuffle(items)
        return items

    def visit_test(self, test):
        pass

    def visit_keyword(self, kw):
        pass
