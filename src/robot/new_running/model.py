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

from robot import model
from robot.output import Output
from robot.conf import RobotSettings

from .randomizer import Randomizer
from .runner import Runner


class Keyword(model.Keyword):
    __slots__ = []
    message_class = None  # TODO: Remove from base model?

    def is_for_loop(self):
        return False

    def is_comment(self):
        return False

    @property
    def keyword(self):
        return self.name

    @property
    def assign(self):
        return []


class TestCase(model.TestCase):
    __slots__ = []
    keyword_class = Keyword


class UserKeywords(object):

    def has_handler(self, name):
        return False

from robot.variables import Variables


class TestSuite(model.TestSuite):
    __slots__ = []
    test_class = TestCase
    keyword_class = Keyword
    variables = Variables()
    user_keywords = UserKeywords()
    status = 'RUNNING'
    imports = []

    def randomize(self, suites=True, tests=True):
        self.visit(Randomizer(suites, tests))

    def run(self, **options):
        runner = Runner(Output(RobotSettings(options)))
        self.visit(runner)
        return runner.result
