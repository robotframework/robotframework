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

import os.path

from robot.conf import RobotSettings
from robot import model
from robot.output import LOGGER, Output, pyloggingconf
from robot.utils import setter
from robot.variables import init_global_variables

from .namespace import IMPORTER
from .randomizer import Randomizer
from .runner import Runner
from .signalhandler import STOP_SIGNAL_MONITOR


class Keyword(model.Keyword):
    message_class = None  # TODO: Remove from base model?

    def __init__(self, name='', args=(), assign=(), type='kw'):
        model.Keyword.__init__(self, name=name, args=args, type=type)
        self.assign = assign

    def is_for_loop(self):
        return False

    def is_comment(self):
        return False

    @property
    def keyword(self):
        return self.name


class ForLoop(Keyword):
    keyword_class = Keyword

    def __init__(self, vars, items, range):
        Keyword.__init__(self, assign=vars, args=items, type='for')
        self.range = range

    @property
    def vars(self):
        return self.assign

    @property
    def items(self):
        return self.args

    def is_for_loop(self):
        return True

    @property
    def steps(self):
        return self.keywords


class TestCase(model.TestCase):
    __slots__ = ['template']
    keyword_class = Keyword

    def __init__(self, name='', doc='', tags=None, timeout=None, template=None):
        model.TestCase.__init__(self, name, doc, tags, timeout)
        self.template = template

    @setter
    def timeout(self, timeout):
        return Timeout(*timeout) if timeout else None


class TestSuite(model.TestSuite):
    __slots__ = []
    test_class = TestCase
    keyword_class = Keyword

    def __init__(self,  name='', doc='', metadata=None, source=None):
        """Running model for single test suite.

        :ivar parent: Parent :class:`TestSuite` or `None`.
        :ivar name: Test suite name.
        :ivar doc: Test suite documentation.
        :ivar metadata: Test suite metadata as a dictionary.
        :ivar source: Path to the source file or directory.
        :ivar suites: Child suites.
        :ivar tests: A list of :class:`~.testcase.TestCase` instances.
        :ivar keywords: A list containing setup and teardown.
        """
        model.TestSuite.__init__(self, name, doc, metadata, source)
        self.imports = []
        self.user_keywords = []
        self.variables = []

    @setter
    def imports(self, imports):
        return model.Imports(self.source, imports)

    @setter
    def user_keywords(self, keywords):
        return model.ItemList(UserKeyword, items=keywords)

    @setter
    def variables(self, variables):
        return model.ItemList(Variable, {'source': self.source}, items=variables)

    def configure(self, randomize_suites=False, randomize_tests=False,
                  **options):
        model.TestSuite.configure(self, **options)
        self.randomize(randomize_suites, randomize_tests)

    def randomize(self, suites=True, tests=True):
        self.visit(Randomizer(suites, tests))

    def run(self, settings=None, **options):
        STOP_SIGNAL_MONITOR.start()
        IMPORTER.reset()
        settings = settings or RobotSettings(options)
        pyloggingconf.initialize(settings['LogLevel'])
        init_global_variables(settings)
        output = Output(settings)
        runner = Runner(output, settings)
        self.visit(runner)
        output.close(runner.result)
        return runner.result


class Variable(object):

    def __init__(self, name, value, source=None):
        # TODO: check name and value
        self.name = name
        self.value = value
        self.source = source

    def report_invalid_syntax(self, message, level='ERROR'):
        LOGGER.write("Error in file '%s': Setting variable '%s' failed: %s"
                     % (self.source or '<unknown>', self.name, message), level)


class Timeout(object):

    def __init__(self, value, message=None):
        self.value = value
        self.message = message

    def __str__(self):
        return self.value


class UserKeyword(object):
    # TODO: In 2.9:
    # - Teardown should be handled as a keyword like with tests and suites.
    # - Timeout should be handled consistently with tests.
    # - Also resource files should use these model objects.

    def __init__(self, name, args=(), doc='', return_=None, timeout=None,
                 teardown=None):
        self.name = name
        self.args = args
        self.doc = doc
        self.return_ = return_ or ()
        self.teardown = None
        self.timeout = timeout
        self.teardown = teardown
        self.keywords = []

    @setter
    def keywords(self, keywords):
        return model.ItemList(Keyword, items=keywords)

    # Compatibility with parsing model. Should be removed in 2.9.
    @property
    def steps(self):
        return self.keywords
