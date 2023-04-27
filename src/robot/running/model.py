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

When tests are executed by Robot Framework, a :class:`TestSuite` structure using
classes defined in this module is created by
:class:`~robot.running.builder.builders.TestSuiteBuilder`
based on data on a file system. In addition to that, external tools can
create executable suite structures programmatically.

Regardless the approach to construct it, a :class:`TestSuite` object is executed
by calling its :meth:`~TestSuite.run` method as shown in the example in
the :mod:`robot.running` package level documentation. When a suite is run,
test, keywords, and other objects it contains can be inspected and modified
by using `pre-run modifiers`__ and `listeners`__.

The :class:`TestSuite` class is exposed via the :mod:`robot.api` package. If other
classes are needed, they can be imported from :mod:`robot.running`.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#programmatic-modification-of-results
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface
"""

import warnings
from pathlib import Path
from typing import TYPE_CHECKING

from robot import model
from robot.conf import RobotSettings
from robot.errors import BreakLoop, ContinueLoop, DataError, ReturnFromKeyword
from robot.model import BodyItem, create_fixture, Keywords, ModelObject
from robot.output import LOGGER, Output, pyloggingconf
from robot.result import (Break as BreakResult, Continue as ContinueResult,
                          Error as ErrorResult, Return as ReturnResult)
from robot.utils import setter

from .bodyrunner import ForRunner, IfRunner, KeywordRunner, TryRunner, WhileRunner
from .randomizer import Randomizer
from .statusreporter import StatusReporter

if TYPE_CHECKING:
    from robot.parsing import File
    from .builder import TestDefaults


class Body(model.Body):
    __slots__ = []


@Body.register
class Keyword(model.Keyword):
    """Represents an executable keyword call.

    A keyword call consists only of a keyword name, arguments and possible
    assignment in the data::

        Keyword    arg
        ${result} =    Another Keyword    arg1    arg2

    The actual keyword that is executed depends on the context where this model
    is executed.
    """
    __slots__ = ['lineno']

    def __init__(self, name='', args=(), assign=(), type=BodyItem.KEYWORD, parent=None,
                 lineno=None):
        super().__init__(name, args, assign, type, parent)
        self.lineno = lineno

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def to_dict(self):
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        return data

    def run(self, context, run=True, templated=None):
        return KeywordRunner(context, run).run(self)


@Body.register
class For(model.For):
    __slots__ = ['lineno', 'error']
    body_class = Body

    def __init__(self, variables=(), flavor='IN', values=(), start=None, mode=None,
                 fill=None, parent=None, lineno=None, error=None):
        super().__init__(variables, flavor, values, start, mode, fill, parent)
        self.lineno = lineno
        self.error = error

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def to_dict(self):
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data

    def run(self, context, run=True, templated=False):
        return ForRunner(context, self.flavor, run, templated).run(self)


@Body.register
class While(model.While):
    __slots__ = ['lineno', 'error']
    body_class = Body

    def __init__(self, condition=None, limit=None, on_limit_message=None,
                 parent=None, lineno=None, error=None):
        super().__init__(condition, limit, on_limit_message, parent)
        self.lineno = lineno
        self.error = error

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def to_dict(self):
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data

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

    def to_dict(self):
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        return data


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

    def to_dict(self):
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


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

    def to_dict(self):
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        return data


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

    def to_dict(self):
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


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
                    raise DataError(self.error, syntax=True)
                if not context.dry_run:
                    raise ReturnFromKeyword(self.values)

    def to_dict(self):
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


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
            if run:
                if self.error:
                    raise DataError(self.error, syntax=True)
                if not context.dry_run:
                    raise ContinueLoop()

    def to_dict(self):
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


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
            if run:
                if self.error:
                    raise DataError(self.error, syntax=True)
                if not context.dry_run:
                    raise BreakLoop()

    def to_dict(self):
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


@Body.register
class Error(model.Error):
    __slots__ = ['lineno', 'error']

    def __init__(self, values=(), parent=None, lineno=None, error=None):
        super().__init__(values, parent)
        self.lineno = lineno
        self.error = error

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def run(self, context, run=True, templated=False):
        with StatusReporter(self, ErrorResult(self.values), context, run):
            if run:
                raise DataError(self.error)

    def to_dict(self):
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


class TestCase(model.TestCase):
    """Represents a single executable test case.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['template', 'error']
    body_class = Body        #: Internal usage only.
    fixture_class = Keyword  #: Internal usage only.

    def __init__(self, name='', doc='', tags=None, timeout=None, template=None,
                 lineno=None, error=None):
        super().__init__(name, doc, tags, timeout, lineno)
        #: Name of the keyword that has been used as a template when building the test.
        # ``None`` if template is not used.
        self.template = template
        self.error = error

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def to_dict(self):
        data = super().to_dict()
        if self.template:
            data['template'] = self.template
        if self.error:
            data['error'] = self.error
        return data


class TestSuite(model.TestSuite):
    """Represents a single executable test suite.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = []
    test_class = TestCase    #: Internal usage only.
    fixture_class = Keyword  #: Internal usage only.

    def __init__(self,  name='', doc='', metadata=None, source=None, rpa=None):
        super().__init__(name, doc, metadata, source, rpa)
        #: :class:`ResourceFile` instance containing imports, variables and
        #: keywords the suite owns. When data is parsed from the file system,
        #: this data comes from the same test case file that creates the suite.
        self.resource = ResourceFile(parent=self)

    @setter
    def resource(self, resource: 'ResourceFile|dict') -> 'ResourceFile':
        if isinstance(resource, dict):
            resource = ResourceFile.from_dict(resource)
            resource.parent = self
        return resource

    @classmethod
    def from_file_system(cls, *paths: 'Path|str', **config) -> 'TestSuite':
        """Create a :class:`TestSuite` object based on the given ``paths``.

        :param paths: File or directory paths where to read the data from.
        :param config: Configuration parameters for :class:`~.builders.TestSuiteBuilder`
            class that is used internally for building the suite.

        See also :meth:`from_model` and :meth:`from_string`.
        """
        from .builder import TestSuiteBuilder
        return TestSuiteBuilder(**config).build(*paths)

    @classmethod
    def from_model(cls, model: 'File', name: 'str|None' = None, *,
                   defaults: 'TestDefaults|None' = None) -> 'TestSuite':
        """Create a :class:`TestSuite` object based on the given ``model``.

        :param model: Model to create the suite from.
        :param name: Deprecated since Robot Framework 6.1.
        :param defaults: Possible test specific defaults from suite
            initialization files. New in Robot Framework 6.1.

        The model can be created by using the
        :func:`~robot.parsing.parser.parser.get_model` function and possibly
        modified by other tooling in the :mod:`robot.parsing` module.

        Giving suite name is deprecated and users should set it and possible
        other attributes to the returned suite separately. One easy way is using
        the :meth:`config` method like this::

            suite = TestSuite.from_model(model).config(name='X', doc='Example')

        See also :meth:`from_file_system` and :meth:`from_string`.
        """
        from .builder import RobotParser
        suite = RobotParser().parse_model(model, defaults)
        if name is not None:
            # TODO: Remove 'name' in RF 7.
            warnings.warn("'name' argument of 'TestSuite.from_model' is deprecated. "
                          "Set the name to the returned suite separately.")
            suite.name = name
        return suite

    @classmethod
    def from_string(cls, string: str, *, defaults: 'TestDefaults|None' = None,
                    **config) -> 'TestSuite':
        """Create a :class:`TestSuite` object based on the given ``string``.

        :param string: String to create the suite from.
        :param defaults: Possible test specific defaults from suite
            initialization files.
        :param config: Configuration parameters for
             :func:`~robot.parsing.parser.parser.get_model` used internally.

        If suite name or other attributes need to be set, an easy way is using
        the :meth:`config` method like this::

            suite = TestSuite.from_string(string).config(name='X', doc='Example')

        New in Robot Framework 6.1. See also :meth:`from_model` and
        :meth:`from_file_system`.
        """
        from robot.parsing import get_model
        model = get_model(string, data_only=True, **config)
        return cls.from_model(model, defaults=defaults)

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
        """Executes the suite based on the given ``settings`` or ``options``.

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

    def to_dict(self):
        data = super().to_dict()
        data['resource'] = self.resource.to_dict()
        return data


class Variable(ModelObject):
    repr_args = ('name', 'value')

    def __init__(self, name, value=(), parent=None, lineno=None, error=None):
        self.name = name
        self.value = value
        self.parent = parent
        self.lineno = lineno
        self.error = error

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def report_invalid_syntax(self, message, level='ERROR'):
        source = self.source or '<unknown>'
        line = f' on line {self.lineno}' if self.lineno else ''
        LOGGER.write(f"Error in file '{source}'{line}: "
                     f"Setting variable '{self.name}' failed: {message}", level)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        data = {'name': self.name, 'value': list(self.value)}
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


class ResourceFile(ModelObject):
    repr_args = ('source',)
    __slots__ = ('_source', 'parent', 'doc')

    def __init__(self, source=None, parent=None, doc=''):
        self._source = source
        self.parent = parent
        self.doc = doc
        self.imports = []
        self.variables = []
        self.keywords = []

    @property
    def source(self):
        if self._source:
            return self._source
        if self.parent:
            return self.parent.source
        return None

    @source.setter
    def source(self, source):
        if not isinstance(source, (Path, type(None))):
            source = Path(source)
        self._source = source

    @setter
    def imports(self, imports):
        return Imports(self, imports)

    @setter
    def variables(self, variables):
        return model.ItemList(Variable, {'parent': self}, items=variables)

    @setter
    def keywords(self, keywords):
        return model.ItemList(UserKeyword, {'parent': self}, items=keywords)

    def to_dict(self):
        data = {}
        if self._source:
            data['source'] = str(self.source)
        if self.doc:
            data['doc'] = self.doc
        if self.imports:
            data['imports'] = self.imports.to_dicts()
        if self.variables:
            data['variables'] = self.variables.to_dicts()
        if self.keywords:
            data['keywords'] = self.keywords.to_dicts()
        return data


class UserKeyword(ModelObject):
    repr_args = ('name', 'args')
    fixture_class = Keyword
    __slots__ = ['name', 'args', 'doc', 'return_', 'timeout', 'lineno', 'parent',
                 'error', '_teardown']

    def __init__(self, name='', args=(), doc='', tags=(), return_=None,
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
            self._teardown = create_fixture(None, self, Keyword.TEARDOWN)
        return self._teardown

    @teardown.setter
    def teardown(self, teardown):
        self._teardown = create_fixture(teardown, self, Keyword.TEARDOWN)

    @property
    def has_teardown(self):
        """Check does a keyword have a teardown without creating a teardown object.

        A difference between using ``if uk.has_teardown:`` and ``if uk.teardown:``
        is that accessing the :attr:`teardown` attribute creates a :class:`Keyword`
        object representing the teardown even when the user keyword actually does
        not have one. This can have an effect on memory usage.

        New in Robot Framework 6.1.
        """
        return bool(self._teardown)

    @setter
    def tags(self, tags):
        return model.Tags(tags)

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def to_dict(self):
        data = {'name': self.name}
        if self.args:
            data['args'] = list(self.args)
        if self.doc:
            data['doc'] = self.doc
        if self.tags:
            data['tags'] = list(self.tags)
        if self.return_:
            data['return_'] = self.return_
        if self.timeout:
            data['timeout'] = self.timeout
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        data['body'] = self.body.to_dicts()
        if self.has_teardown:
            data['teardown'] = self.teardown.to_dict()
        return data


class Import(ModelObject):
    repr_args = ('type', 'name', 'args', 'alias')
    LIBRARY = 'LIBRARY'
    RESOURCE = 'RESOURCE'
    VARIABLES = 'VARIABLES'

    def __init__(self, type, name, args=(), alias=None, parent=None, lineno=None):
        if type not in (self.LIBRARY, self.RESOURCE, self.VARIABLES):
            raise ValueError(f"Invalid import type: Expected '{self.LIBRARY}', "
                             f"'{self.RESOURCE}' or '{self.VARIABLES}', got '{type}'.")
        self.type = type
        self.name = name
        self.args = args
        self.alias = alias
        self.parent = parent
        self.lineno = lineno

    @property
    def source(self) -> Path:
        return self.parent.source if self.parent is not None else None

    @property
    def directory(self) -> Path:
        source = self.source
        return source.parent if source and not source.is_dir() else source

    @property
    def setting_name(self):
        return self.type.title()

    def select(self, library, resource, variables):
        return {self.LIBRARY: library,
                self.RESOURCE: resource,
                self.VARIABLES: variables}[self.type]

    def report_invalid_syntax(self, message, level='ERROR'):
        source = self.source or '<unknown>'
        line = f' on line {self.lineno}' if self.lineno else ''
        LOGGER.write(f"Error in file '{source}'{line}: {message}", level)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        data = {'type': self.type, 'name': self.name}
        if self.args:
            data['args'] = list(self.args)
        if self.alias:
            data['alias'] = self.alias
        if self.lineno:
            data['lineno'] = self.lineno
        return data

    def _include_in_repr(self, name, value):
        return name in ('type', 'name') or value


class Imports(model.ItemList):

    def __init__(self, parent, imports=None):
        super().__init__(Import, {'parent': parent}, items=imports)

    def library(self, name, args=(), alias=None, lineno=None):
        """Create library import."""
        self.create(Import.LIBRARY, name, args, alias, lineno=lineno)

    def resource(self, name, lineno=None):
        """Create resource import."""
        self.create(Import.RESOURCE, name, lineno=lineno)

    def variables(self, name, args=(), lineno=None):
        """Create variables import."""
        self.create(Import.VARIABLES, name, args, lineno=lineno)

    def create(self, *args, **kwargs):
        """Generic method for creating imports.

        Import type specific methods :meth:`library`, :meth:`resource` and
        :meth:`variables` are recommended over this method.
        """
        # RF 6.1 changed types to upper case. Code below adds backwards compatibility.
        if args:
            args = (args[0].upper(),) + args[1:]
        elif 'type' in kwargs:
            kwargs['type'] = kwargs['type'].upper()
        return super().create(*args, **kwargs)
