#  Copyright 2008-2015 Nokia Solutions and Networks
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

from random import Random

from robot.model import SuiteVisitor


class Randomizer(SuiteVisitor):

    def __init__(self, randomize_suites=True, randomize_tests=True, seed=None):
        self.randomize_suites = randomize_suites
        self.randomize_tests = randomize_tests
        self.seed = seed
        # Cannot use just Random(seed) due to
        # https://ironpython.codeplex.com/workitem/35155
        args = (seed,) if seed is not None else ()
        self._shuffle = Random(*args).shuffle

    def start_suite(self, suite):
        if not self.randomize_suites and not self.randomize_tests:
            return False
        if self.randomize_suites:
            self._shuffle(suite.suites)
        if self.randomize_tests:
            self._shuffle(suite.tests)
        if not suite.parent:
            suite.metadata['Randomized'] = self._get_message()

    def _get_message(self):
        possibilities = {(True, True): 'Suites and tests',
                         (True, False): 'Suites',
                         (False, True): 'Tests'}
        randomized = (self.randomize_suites, self.randomize_tests)
        return '%s (seed %s)' % (possibilities[randomized], self.seed)

    def visit_test(self, test):
        pass

    def visit_keyword(self, kw):
        pass
