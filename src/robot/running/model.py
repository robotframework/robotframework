#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

import os

from robot import model
from robot.conf import RobotSettings
from robot.errors import BreakLoop, ContinueLoop, ReturnFromKeyword, DataError
from robot.model import Keywords, BodyItem
from robot.output import LOGGER, Output, pyloggingconf
from robot.result import (Break as BreakResult, Continue as ContinueResult,
                          Return as ReturnResult)
from robot.utils import seq2str, setter

from .bodyrunner import ForRunner, IfRunner, KeywordRunner, TryRunner, WhileRunner
from .randomizer import Randomizer
from .statusreporter import StatusReporter


class Body(model.Body):
    __slots__ = []


@Body.register
class Keyword(model.Keyword):
    """Represents a single executable keyword.

    These keywords never have child keywords or messages. The actual keyword
    that is executed depends on the context where this model is executed.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['lineno']

    def __init__(self, name='', doc='', args=(), assign=(), tags=(), timeout=None,
                 type=BodyItem.KEYWORD, parent=None, lineno=None):
        super().__init__(name, doc, args, assign, tags, timeout, type, parent)
        self.lineno = lineno

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def run(self, context, run=True, templated=None):
        return KeywordRunner(context, run).run(self)


@Body.register
class For(model.For):
    __slots__ = ['lineno', 'error']
    body_class = Body

    def __init__(self, variables, flavor, values, parent=None, lineno=None, error=None):
        super().__init__(variables, flavor, values, parent)
        self.lineno = lineno
        self.error = error

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def run(self, context, run=True, templated=False):
        return ForRunner(context, self.flavor, run, templated).run(self)


@Body.register
class While(model.While):
    __slots__ = ['lineno', 'error']
    body_class = Body

    def __init__(self, condition=None, limit=None, parent=None, lineno=None, error=None):
        super().__init__(condition, limit, parent)
        self.lineno = lineno
        self.error = error

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def run(self, context, run=True, templated=False):
        return WhileRunner(context, run, templated).run(self)


class IfBranch(model.IfBranch):
    __slots__ = ['lineno']
    body_class = Body

    def __init__(self, type=BodyItem.IF, condition=None, parent=None, lineno=None):
        super().__init__(type, condition, parent)
        self.lineno = lineno

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None


@Body.register
class If(model.If):
    __slots__ = ['lineno', 'error']
    branch_class = IfBranch

    def __init__(self, parent=None, lineno=None, error=None):
        super().__init__(parent)
        self.lineno = lineno
        self.error = error

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def run(self, context, run=True, templated=False):
        return IfRunner(context, run, templated).run(self)


class TryBranch(model.TryBranch):
    __slots__ = ['lineno']
    body_class = Body

    def __init__(self, type=BodyItem.TRY, patterns=(), pattern_type=None,
                 variable=None, parent=None, lineno=None):
        super().__init__(type, patterns, pattern_type, variable, parent)
        self.lineno = lineno

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None


@Body.register
class Try(model.Try):
    __slots__ = ['lineno', 'error']
    branch_class = TryBranch

    def __init__(self, parent=None, lineno=None, error=None):
        super().__init__(parent)
        self.lineno = lineno
        self.error = error

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def run(self, context, run=True, templated=False):
        return TryRunner(context, run, templated).run(self)


@Body.register
class Return(model.Return):
    __slots__ = ['lineno', 'error']

    def __init__(self, values=(), parent=None, lineno=None, error=None):
        super().__init__(values, parent)
        self.lineno = lineno
        self.error = error

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def run(self, context, run=True, templated=False):
        with StatusReporter(self, ReturnResult(self.values), context, run):
            if run:
                if self.error:
                    raise DataError(self.error)
                raise ReturnFromKeyword(self.values)


@Body.register
class Continue(model.Continue):
    __slots__ = ['lineno', 'error']

    def __init__(self, parent=None, lineno=None, error=None):
        super().__init__(parent)
        self.lineno = lineno
        self.error = error

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def run(self, context, run=True, templated=False):
        with StatusReporter(self, ContinueResult(), context, run):
            if self.error:
                raise DataError(self.error)
            if run:
                raise ContinueLoop()


@Body.register
class Break(model.Break):
    __slots__ = ['lineno', 'error']

    def __init__(self, parent=None, lineno=None, error=None):
        super().__init__(parent)
        self.lineno = lineno
        self.error = error

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def run(self, context, run=True, templated=False):
        with StatusReporter(self, BreakResult(), context, run):
            if self.error:
                raise DataError(self.error)
            if run:
                raise BreakLoop()


class TestCase(model.TestCase):
    """Represents a single executable test case.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['template']
    body_class = Body        #: Internal usage only.
    fixture_class = Keyword  #: Internal usage only.

    def __init__(self, name='', doc='', tags=None, timeout=None, template=None,
                 lineno=None):
        super().__init__(name, doc, tags, timeout, lineno)
        #: Name of the keyword that has been used as a template when building the test.
        # ``None`` if template is not used.
        self.template = template

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None


class TestSuite(model.TestSuite):
    """Represents a single executable test suite.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['resource']
    test_class = TestCase    #: Internal usage only.
    fixture_class = Keyword  #: Internal usage only.

    def __init__(self,  name='', doc='', metadata=None, source=None, rpa=None):
        super().__init__(name, doc, metadata, source, rpa)
        #: :class:`ResourceFile` instance containing imports, variables and
        #: keywords the suite owns. When data is parsed from the file system,
        #: this data comes from the same test case file that creates the suite.
        self.resource = ResourceFile(source=source)

    @classmethod
    def from_file_system(cls, *paths, **config):
        """Create a :class:`TestSuite` object based on the given ``paths``.

        ``paths`` are file or directory paths where to read the data from.

        Internally utilizes the :class:`~.builders.TestSuiteBuilder` class
        and ``config`` can be used to configure how it is initialized.

        New in Robot Framework 3.2.
        """
        from .builder import TestSuiteBuilder
        return TestSuiteBuilder(**config).build(*paths)

    @classmethod
    def from_model(cls, model, name=None):
        """Create a :class:`TestSuite` object based on the given ``model``.

        The model can be created by using the
        :func:`~robot.parsing.parser.parser.get_model` function and possibly
        modified by other tooling in the :mod:`robot.parsing` module.

        New in Robot Framework 3.2.
        """
        from .builder import RobotParser
        return RobotParser().build_suite(model, name)

    def configure(self, randomize_suites=False, randomize_tests=False,
                  randomize_seed=None, **options):
        """A shortcut to configure a suite using one method call.

        Can only be used with the root test suite.

        :param randomize_xxx: Passed to :meth:`randomize`.
        :param options: Passed to
            :class:`~robot.model.configurer.SuiteConfigurer` that will then
            set suite attributes, call :meth:`filter`, etc. as needed.

        Example::

            suite.configure(included_tags=['smoke'],
                            doc='Smoke test results.')

        Not to be confused with :meth:`config` method that suites, tests,
        and keywords have to make it possible to set multiple attributes in
        one call.
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
        options except without hyphens. Some options are ignored (see below),
        but otherwise they have the same semantics as on the command line.
        Options that can be given on the command line multiple times can be
        passed as lists like ``variable=['VAR1:value1', 'VAR2:value2']``.
        If such an option is used only once, it can be given also as a single
        string like ``variable='VAR:value'``.

        Additionally listener option allows passing object directly instead of
        listener name, e.g. ``run('tests.robot', listener=Listener())``.

        To capture stdout and/or stderr streams, pass open file objects in as
        special keyword arguments ``stdout`` and ``stderr``, respectively.

        Only options related to the actual test execution have an effect.
        For example, options related to selecting or modifying test cases or
        suites (e.g. ``--include``, ``--name``, ``--prerunmodifier``) or
        creating logs and reports are silently ignored. The output XML
        generated as part of the execution can be configured, though. This
        includes disabling it with ``output=None``.

        Example::

            stdout = StringIO()
            result = suite.run(variable='EXAMPLE:value',
                               output='example.xml',
                               exitonfailure=True,
                               stdout=stdout)
            print(result.return_code)

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
        from .suiterunner import SuiteRunner

        with LOGGER:
            if not settings:
                settings = RobotSettings(options)
                LOGGER.register_console_logger(**settings.console_output_config)
            with pyloggingconf.robot_handler_enabled(settings.log_level):
                with STOP_SIGNAL_MONITOR:
                    IMPORTER.reset()
                    output = Output(settings)
                    runner = SuiteRunner(output, settings)
                    self.visit(runner)
                output.close(runner.result)
        return runner.result


class Variable:

    def __init__(self, name, value, source=None, lineno=None, error=None):
        self.name = name
        self.value = value
        self.source = source
        self.lineno = lineno
        self.error = error

    def report_invalid_syntax(self, message, level='ERROR'):
        source = self.source or '<unknown>'
        line = ' on line %s' % self.lineno if self.lineno is not None else ''
        LOGGER.write("Error in file '%s'%s: Setting variable '%s' failed: %s"
                     % (source, line, self.name, message), level)


class ResourceFile:

    def __init__(self, doc='', source=None):
        self.doc = doc
        self.source = source
        self.imports = []
        self.keywords = []
        self.variables = []

    @setter
    def imports(self, imports):
        return Imports(self.source, imports)

    @setter
    def keywords(self, keywords):
        return model.ItemList(UserKeyword, {'parent': self}, items=keywords)

    @setter
    def variables(self, variables):
        return model.ItemList(Variable, {'source': self.source}, items=variables)


class UserKeyword:

    def __init__(self, name, args=(), doc='', tags=(), return_=None,
                 timeout=None, lineno=None, parent=None, error=None):
        self.name = name
        self.args = args
        self.doc = doc
        self.tags = tags
        self.return_ = return_ or ()
        self.timeout = timeout
        self.lineno = lineno
        self.parent = parent
        self.error = error
        self.body = None
        self._teardown = None

    @setter
    def body(self, body):
        """Child keywords as a :class:`~.Body` object."""
        return Body(self, body)

    @property
    def keywords(self):
        """Deprecated since Robot Framework 4.0.

        Use :attr:`body` or :attr:`teardown` instead.
        """
        kws = list(self.body)
        if self.teardown:
            kws.append(self.teardown)
        return Keywords(self, kws)

    @keywords.setter
    def keywords(self, keywords):
        Keywords.raise_deprecation_error()

    @property
    def teardown(self):
        if self._teardown is None:
            self._teardown = Keyword(None, parent=self, type=Keyword.TEARDOWN)
        return self._teardown

    @setter
    def tags(self, tags):
        return model.Tags(tags)

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None


class Import:
    ALLOWED_TYPES = ('Library', 'Resource', 'Variables')

    def __init__(self, type, name, args=(), alias=None, source=None, lineno=None):
        if type not in self.ALLOWED_TYPES:
            raise ValueError("Invalid import type '%s'. Should be one of %s."
                             % (type, seq2str(self.ALLOWED_TYPES, lastsep=' or ')))
        self.type = type
        self.name = name
        self.args = args
        self.alias = alias
        self.source = source
        self.lineno = lineno

    @property
    def directory(self):
        if not self.source:
            return None
        if os.path.isdir(self.source):
            return self.source
        return os.path.dirname(self.source)

    def report_invalid_syntax(self, message, level='ERROR'):
        source = self.source or '<unknown>'
        line = ' on line %s' % self.lineno if self.lineno is not None else ''
        LOGGER.write("Error in file '%s'%s: %s" % (source, line, message), level)


class Imports(model.ItemList):

    def __init__(self, source, imports=None):
        super().__init__(Import, {'source': source}, items=imports)

    def library(self, name, args=(), alias=None, lineno=None):
        self.create('Library', name, args, alias, lineno)

    def resource(self, path, lineno=None):
        self.create('Resource', path, lineno)

    def variables(self, path, args=(), lineno=None):
        self.create('Variables', path, args, lineno)
