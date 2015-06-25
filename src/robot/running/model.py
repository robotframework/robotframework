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

from robot import model
from robot.conf import RobotSettings
from robot.output import LOGGER, Output, pyloggingconf
from robot.utils import setter

from .randomizer import Randomizer


class Keyword(model.Keyword):
    """Running model for single keyword."""
    __slots__ = []
    message_class = None  # TODO: Remove from base model?

    def run(self, context):
        from .keywordrunner import KeywordRunner
        return KeywordRunner(context).run_keyword(self)


class ForLoop(Keyword):
    __slots__ = ['flavor']
    keyword_class = Keyword

    def __init__(self, variables, values, flavor):
        Keyword.__init__(self, assign=variables, args=values,
                         type=Keyword.FOR_LOOP_TYPE)
        self.flavor = flavor

    @property
    def variables(self):
        return self.assign

    @property
    def values(self):
        return self.args


class TestCase(model.TestCase):
    """Running model for single test case."""
    __slots__ = ['template']
    keyword_class = Keyword

    def __init__(self, name='', doc='', tags=None, timeout=None, template=None):
        model.TestCase.__init__(self, name, doc, tags, timeout)
        #: Name of the keyword that has been used as template
        #: when building the test. `None` if no is template used.
        self.template = template

    @setter
    def timeout(self, timeout):
        """Timeout limit of the test case as an instance of
        :class:`~.Timeout.
        """
        return Timeout(*timeout) if timeout else None


class TestSuite(model.TestSuite):
    """Running model for single test suite."""
    __slots__ = ['resource']
    test_class = TestCase
    keyword_class = Keyword

    def __init__(self,  name='', doc='', metadata=None, source=None):
        model.TestSuite.__init__(self, name, doc, metadata, source)
        self.resource = ResourceFile(source=source)

    def configure(self, randomize_suites=False, randomize_tests=False,
                  randomize_seed=None, **options):
        model.TestSuite.configure(self, **options)
        self.randomize(randomize_suites, randomize_tests, randomize_seed)

    def randomize(self, suites=True, tests=True, seed=None):
        """Randomizes the order of suites and/or tests, recursively."""
        self.visit(Randomizer(suites, tests, seed))

    def run(self, settings=None, **options):
        """Executes the suite based based the given ``settings`` or ``options``.

        :param settings: :class:`~robot.conf.settings.RobotSettings` object
            to configure test execution.
        :param options: Used to construct new
            :class:`~robot.conf.settings.RobotSettings` object if ``settings``
            are not given.
        :return: :class:`~robot.result.executionresult.Result` object with
            information about executed suites and tests.

        If ``options`` are used, their names are the same as long command line
        options except without hyphens, and they also have the same semantics.
        Options that can be given on the command line multiple times can be
        passed as lists like ``variable=['VAR1:value1', 'VAR2:value2']``.
        If such an option is used only once, it can be given also as a single
        string like ``variable='VAR:value'``.

        Additionally listener option allows passing object directly instead of
        listener name, e.g. `run('tests.robot', listener=Listener())`.

        To capture stdout and/or stderr streams, pass open file objects in as
        special keyword arguments `stdout` and `stderr`, respectively. Note
        that this works only in version 2.8.4 and newer.

        Only options related to the actual test execution have an effect.
        For example, options related to selecting test cases or creating
        logs and reports are silently ignored. The output XML generated
        as part of the execution can be configured, though. This includes
        disabling it with ``output=None``.

        Example::

            stdout = StringIO()
            result = suite.run(variable='EXAMPLE:value',
                               critical='regression',
                               output='example.xml',
                               exitonfailure=True,
                               stdout=stdout)
            print result.return_code

        To save memory, the returned
        :class:`~robot.result.executionresult.Result` object does not
        have any information about the executed keywords. If that information
        is needed, the created output XML file needs to be read  using the
        :class:`~robot.result.resultbuilder.ExecutionResult` factory method.

        See the :mod:`package level <robot.running>` documentation for
        more examples, including how to construct executable test suites and
        how to create logs and reports based on the execution results.

        See the :func:`robot.run <robot.run.run>` function for a higher-level
        API for executing tests in files or directories.
        """
        from .namespace import IMPORTER
        from .signalhandler import STOP_SIGNAL_MONITOR
        from .runner import Runner

        with LOGGER:
            if not settings:
                settings = RobotSettings(options)
                LOGGER.register_console_logger(**settings.console_output_config)
            with pyloggingconf.robot_handler_enabled(settings.log_level):
                with STOP_SIGNAL_MONITOR:
                    IMPORTER.reset()
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


class ResourceFile(object):

    def __init__(self, doc='', source=None):
        self.doc = doc
        self.source = source
        self.imports = []
        self.keywords = []
        self.variables = []

    @setter
    def imports(self, imports):
        return model.Imports(self.source, imports)

    @setter
    def keywords(self, keywords):
        return model.ItemList(UserKeyword, items=keywords)

    @setter
    def variables(self, variables):
        return model.ItemList(Variable, {'source': self.source}, items=variables)


class UserKeyword(object):

    def __init__(self, name, args=(), doc='', tags=(), return_=None, timeout=None):
        self.name = name
        self.args = args
        self.doc = doc
        self.tags = tags
        self.return_ = return_ or ()
        self.timeout = timeout
        self.keywords = []

    @setter
    def keywords(self, keywords):
        return model.Keywords(Keyword, self, keywords)

    @setter
    def timeout(self, timeout):
        """Timeout limit of the keyword as an instance of
        :class:`~.Timeout.
        """
        return Timeout(*timeout) if timeout else None

    @setter
    def tags(self, tags):
        return model.Tags(tags)
