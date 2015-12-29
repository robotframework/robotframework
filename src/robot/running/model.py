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

"""Module implementing test execution related model objects.

When tests are executed normally, these objects are created based on the test
data on the file system by :class:`~.builder.TestSuiteBuilder`, but external
tools can also create an executable test suite model structure directly.
Regardless the approach to create it, the model is executed by calling
:meth:`~TestSuite.run` method of the root test suite. See the
:mod:`robot.running` package level documentation for more information and
examples.

The most important classes defined in this module are :class:`TestSuite`,
:class:`TestCase` and :class:`Keyword`. When tests are executed, these objects
can be inspected and modified by `pre-run modifiers`__ and `listeners`__.
The aforementioned objects are considered stable, but other objects in this
module may still be changed in the future major releases.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#programmatic-modification-of-results
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface
"""

import warnings

from robot import model
from robot.conf import RobotSettings
from robot.output import LOGGER, Output, pyloggingconf
from robot.utils import setter

from .steprunner import StepRunner
from .randomizer import Randomizer


class Keyword(model.Keyword):
    """Represents a single executable keyword.

    These keywords never have child keywords or messages. The actual keyword
    that is executed depends on the context where this model is executed.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = []
    message_class = None  #: Internal usage only.

    def run(self, context):
        """Execute the keyword.

        Typically called internally by :meth:`TestSuite.run`.
        """
        return StepRunner(context).run_step(self)


class ForLoop(Keyword):
    """Represents a for loop in test data.

    Contains keywords in the loop body as child :attr:`keywords`.
    """
    __slots__ = ['flavor']
    keyword_class = Keyword  #: Internal usage only.

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
    """Represents a single executable test case.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['template']
    keyword_class = Keyword  #: Internal usage only.

    def __init__(self, name='', doc='', tags=None, timeout=None, template=None):
        model.TestCase.__init__(self, name, doc, tags, timeout)
        #: Name of the keyword that has been used as template
        #: when building the test. ``None`` if no is template used.
        self.template = template

    @setter
    def timeout(self, timeout):
        """Test timeout as a :class:`Timeout` instance or ``None``.

        This attribute is likely to change in the future.
        """
        return Timeout(*timeout) if timeout else None


class TestSuite(model.TestSuite):
    """Represents a single executable test suite.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['resource']
    test_class = TestCase    #: Internal usage only.
    keyword_class = Keyword  #: Internal usage only.

    def __init__(self,  name='', doc='', metadata=None, source=None):
        model.TestSuite.__init__(self, name, doc, metadata, source)
        #: :class:`ResourceFile` instance containing imports, variables and
        #: keywords the suite owns. When data is parsed from the file system,
        #: this data comes from the same test case file that creates the suite.
        self.resource = ResourceFile(source=source)

    # TODO: Remote deprecated propertys below in RF 3.1.
    # `TestSuite`.resource was introduced already in RF 2.9.

    @property
    def imports(self):
        """Deprecated. Use ``TestSuite.resource.imports`` instead."""
        warnings.warn("'TestSuite.imports' is deprecated since RF 2.9. "
                      "Use 'TestSuite.resource.imports' instead.",
                      UserWarning)
        return self.resource.imports

    @property
    def variables(self):
        """Deprecated. Use ``TestSuite.resource.variables`` instead."""
        warnings.warn("'TestSuite.variables' is deprecated since RF 2.9. "
                      "Use 'TestSuite.resource.variables' instead.",
                      UserWarning)
        return self.resource.variables

    @property
    def user_keywords(self):
        """Deprecated. Use ``TestSuite.resource.keywords`` instead."""
        warnings.warn("'TestSuite.user_keywords' is deprecated since RF 2.9. "
                      "Use 'TestSuite.resource.keywords' instead.",
                      UserWarning)
        return self.resource.keywords

    def configure(self, randomize_suites=False, randomize_tests=False,
                  randomize_seed=None, **options):
        """A shortcut to configure a suite using one method call.

        :param randomize_xxx: Passed to :meth:`randomize`.
        :param options: Passed to
            :class:`~robot.model.configurer.SuiteConfigurer` that will then
            set suite attributes, call :meth:`filter`, etc. as needed.

        Example::

            suite.configure(included_tags=['smoke'],
                            doc='Smoke test results.')
        """
        model.TestSuite.configure(self, **options)
        self.randomize(randomize_suites, randomize_tests, randomize_seed)

    def randomize(self, suites=True, tests=True, seed=None):
        """Randomizes the order of suites and/or tests, recursively.

        :param suites: Boolean controlling should suites be randomized.
        :param tests: Boolean controlling should tests be randomized.
        :param seed: Random seed. Can be given if previous random order needs
            to be re-created. Seed value is always shown in logs and reports.
        """
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
        listener name, e.g. ``run('tests.robot', listener=Listener())``.

        To capture stdout and/or stderr streams, pass open file objects in as
        special keyword arguments ``stdout`` and ``stderr``, respectively.
        Note that this works only in version 2.8.4 and newer.

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
        """Keyword timeout as a :class:`Timeout` instance or ``None``."""
        return Timeout(*timeout) if timeout else None

    @setter
    def tags(self, tags):
        return model.Tags(tags)
