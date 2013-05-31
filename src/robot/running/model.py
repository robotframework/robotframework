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

from robot import model
from robot.output import LOGGER
from robot.utils import setter

from .randomizer import Randomizer
from .runner import Runner


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

    # TODO: Remove compatibility
    def apply_template(self, template):
        return self


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

    # TODO: Remove compatibility
    def apply_template(self, template):
        return self


class TestCase(model.TestCase):
    __slots__ = ['template']
    keyword_class = Keyword

    def __init__(self, template=None, **kwargs):
        model.TestCase.__init__(self, **kwargs)
        self.template = template

    @setter
    def timeout(self, timeout):
        return Timeout(*timeout) if timeout else None


class TestSuite(model.TestSuite):
    __slots__ = []
    test_class = TestCase
    keyword_class = Keyword
    status = 'RUNNING'   # TODO: Remove compatibility

    def __init__(self, **kwargs):
        model.TestSuite.__init__(self, **kwargs)
        self.imports = []
        self.user_keywords = []
        self.variables = []

    @setter
    def imports(self, imports):
        return model.ItemList(Import, {'source': self.source}, items=imports)

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
        from robot.conf import RobotSettings
        from robot.output import LOGGER, Output, pyloggingconf
        from robot.running import STOP_SIGNAL_MONITOR, namespace
        from robot.variables import init_global_variables

        STOP_SIGNAL_MONITOR.start()
        namespace.IMPORTER.reset()
        settings = settings or RobotSettings(options)
        pyloggingconf.initialize(settings['LogLevel'])
        init_global_variables(settings)
        output = Output(settings)
        runner = Runner(output, settings)
        self.visit(runner)
        output.close(runner.result)
        return runner.result

    # TODO: Remove compatibility with old model
    def _set_critical_tags(self, arg):
        pass
    critical = None


class Variable(object):

    def __init__(self, name, value, source=None):
        # TODO: check name and value
        self.name = name
        self.value = value
        self.source = source

    def report_invalid_syntax(self, message, level='ERROR'):
        # TODO: Remove table information here and elsewhere
        LOGGER.write("Error in file '%s' in table 'Variables': "
                     "Setting variable '%s' failed: %s"
                     % (self.source or '<unknown>', self.name, message), level)


class Timeout(object):

    def __init__(self, value, message=None):
        self.value = value
        self.message = message

    def __str__(self):
        return self.value


class UserKeyword(object):
    # TODO: Teardown should be handled as a keyword like with tests and suites.
    # Cannot easily do it until running user keywords is "modernized".

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

    # TODO: Remove compatibility
    @property
    def steps(self):
        return self.keywords


class Import(object):

    # TODO: Should type be verified?
    # TODO: Should we have separate methods for adding libs, resources, vars?
    def __init__(self, type, name, args=(), alias=None, source=None):
        self.type = type
        self.name = name
        self.args = args
        self.alias = alias
        self.source = source

    @property
    def directory(self):
        if not self.source:
            return None
        if os.path.isdir(self.source):
            return self.source
        return os.path.dirname(self.source)

    def report_invalid_syntax(self, message, level='ERROR'):
        # TODO: Remove table information from error message here and
        # also from _TestData.report_invalid_syntax in parsing/model.py
        LOGGER.write("Error in file '%s' in table 'Settings': %s"
                     % (self.source or '<unknown>', message), level)
