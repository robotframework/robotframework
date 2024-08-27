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
from typing import Any, Literal, Mapping, Sequence, TYPE_CHECKING, TypeVar, Union

from robot import model
from robot.conf import RobotSettings
from robot.errors import BreakLoop, ContinueLoop, DataError, ReturnFromKeyword, VariableError
from robot.model import BodyItem, DataDict, TestSuites
from robot.output import LOGGER, Output, pyloggingconf
from robot.utils import format_assign_message, setter
from robot.variables import VariableResolver

from .bodyrunner import ForRunner, IfRunner, KeywordRunner, TryRunner, WhileRunner
from .randomizer import Randomizer
from .statusreporter import StatusReporter

if TYPE_CHECKING:
    from robot.parsing import File
    from .builder import TestDefaults
    from .resourcemodel import ResourceFile, UserKeyword


IT = TypeVar('IT', bound='IfBranch|TryBranch')
BodyItemParent = Union['TestSuite', 'TestCase', 'UserKeyword', 'For', 'If', 'IfBranch',
                       'Try', 'TryBranch', 'While', None]


class Body(model.BaseBody['Keyword', 'For', 'While', 'If', 'Try', 'Var', 'Return',
                          'Continue', 'Break', 'model.Message', 'Error']):
    __slots__ = ()


class Branches(model.BaseBranches['Keyword', 'For', 'While', 'If', 'Try', 'Var', 'Return',
                                  'Continue', 'Break', 'model.Message', 'Error', IT]):
    __slots__ = ()


class WithSource:
    __slots__ = ()
    parent: BodyItemParent

    @property
    def source(self) -> 'Path|None':
        return self.parent.source if self.parent is not None else None


class Argument:
    """A temporary API for creating named arguments with non-string values.

    This class was added in RF 7.0.1 (#5031) after a failed attempt to add a public
    API for this purpose in RF 7.0 (#5000). A better public API that allows passing
    named arguments separately was added in RF 7.1 (#5143).

    If you need to support also RF 7.0, you can pass named arguments as two-item tuples
    like `(name, value)` and positional arguments as one-item tuples like `(value,)`.
    That approach does not work anymore in RF 7.0.1, though, so the code needs to be
    conditional depending on Robot Framework version.

    The main limitation of this class is that it is not compatible with the JSON model.
    The current plan is to remove this in the future, possibly already in RF 8.0, but
    we can consider preserving it if it turns out to be useful.
    """

    def __init__(self, name: 'str|None', value: Any):
        """
        :param name: Argument name. If ``None``, argument is considered positional.
        :param value: Argument value.
        """
        self.name = name
        self.value = value

    def __str__(self):
        return str(self.value) if self.name is None else f'{self.name}={self.value}'


@Body.register
class Keyword(model.Keyword, WithSource):
    """Represents an executable keyword call.

    A keyword call consists only of a keyword name, arguments and possible
    assignment in the data::

        Keyword    arg
        ${result} =    Another Keyword    arg1    arg2

    The actual keyword that is executed depends on the context where this model
    is executed.

    Arguments originating from normal Robot Framework data are stored in the
    :attr:`args` attribute as a tuple of strings in the exact same format as in
    the data. This means that arguments can have variables and escape characters,
    and that named arguments are specified using the ``name=value`` syntax.

    When creating keywords programmatically, it is possible to set :attr:`named_args`
    separately and use :attr:`args` only for positional arguments. Argument values
    do not need to be strings, but also in this case strings can contain variables
    and normal Robot Framework escaping rules must be taken into account.
    """
    __slots__ = ['named_args', 'lineno']

    def __init__(self, name: str = '',
                 args: 'Sequence[str|Argument|Any]' = (),
                 named_args: 'Mapping[str, Any]|None' = None,
                 assign: Sequence[str] = (),
                 type: str = BodyItem.KEYWORD,
                 parent: BodyItemParent = None,
                 lineno: 'int|None' = None):
        super().__init__(name, args, assign, type, parent)
        self.named_args = named_args
        self.lineno = lineno

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.named_args is not None:
            data['named_args'] = self.named_args
        if self.lineno:
            data['lineno'] = self.lineno
        return data

    def run(self, result, context, run=True, templated=None):
        return KeywordRunner(context, run).run(self, result.body.create_keyword())


class ForIteration(model.ForIteration, WithSource):
    __slots__ = ('lineno', 'error')
    body_class = Body

    def __init__(self, assign: 'Mapping[str, str]|None' = None,
                 parent: BodyItemParent = None,
                 lineno: 'int|None' = None,
                 error: 'str|None' = None):
        super().__init__(assign, parent)
        self.lineno = lineno
        self.error = error


@Body.register
class For(model.For, WithSource):
    __slots__ = ['lineno', 'error']
    body_class = Body

    def __init__(self, assign: Sequence[str] = (),
                 flavor: Literal['IN', 'IN RANGE', 'IN ENUMERATE', 'IN ZIP'] = 'IN',
                 values: Sequence[str] = (),
                 start: 'str|None' = None,
                 mode: 'str|None' = None,
                 fill: 'str|None' = None,
                 parent: BodyItemParent = None,
                 lineno: 'int|None' = None,
                 error: 'str|None' = None):
        super().__init__(assign, flavor, values, start, mode, fill, parent)
        self.lineno = lineno
        self.error = error

    @classmethod
    def from_dict(cls, data: DataDict) -> 'For':
        # RF 6.1 compatibility
        if 'variables' in data:
            data['assign'] = data.pop('variables')
        return super().from_dict(data)

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data

    def run(self, result, context, run=True, templated=False):
        result = result.body.create_for(self.assign, self.flavor, self.values,
                                        self.start, self.mode, self.fill)
        return ForRunner(context, self.flavor, run, templated).run(self, result)

    def get_iteration(self, assign: 'Mapping[str, str]|None' = None) -> ForIteration:
        iteration = ForIteration(assign, self, self.lineno, self.error)
        iteration.body = [item.to_dict() for item in self.body]
        return iteration


class WhileIteration(model.WhileIteration, WithSource):
    __slots__ = ('lineno', 'error')
    body_class = Body

    def __init__(self, parent: BodyItemParent = None,
                 lineno: 'int|None' = None,
                 error: 'str|None' = None):
        super().__init__(parent)
        self.lineno = lineno
        self.error = error


@Body.register
class While(model.While, WithSource):
    __slots__ = ['lineno', 'error']
    body_class = Body

    def __init__(self, condition: 'str|None' = None,
                 limit: 'str|None' = None,
                 on_limit: 'str|None' = None,
                 on_limit_message: 'str|None' = None,
                 parent: BodyItemParent = None,
                 lineno: 'int|None' = None,
                 error: 'str|None' = None):
        super().__init__(condition, limit, on_limit, on_limit_message, parent)
        self.lineno = lineno
        self.error = error

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data

    def run(self, result, context, run=True, templated=False):
        result = result.body.create_while(self.condition, self.limit, self.on_limit,
                                          self.on_limit_message)
        return WhileRunner(context, run, templated).run(self, result)

    def get_iteration(self) -> WhileIteration:
        iteration = WhileIteration(self, self.lineno, self.error)
        iteration.body = [item.to_dict() for item in self.body]
        return iteration


class IfBranch(model.IfBranch, WithSource):
    body_class = Body
    __slots__ = ['lineno']

    def __init__(self, type: str = BodyItem.IF,
                 condition: 'str|None' = None,
                 parent: BodyItemParent = None,
                 lineno: 'int|None' = None):
        super().__init__(type, condition, parent)
        self.lineno = lineno

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        return data


@Body.register
class If(model.If, WithSource):
    branch_class = IfBranch
    branches_class = Branches[branch_class]
    __slots__ = ['lineno', 'error']

    def __init__(self, parent: BodyItemParent = None,
                 lineno: 'int|None' = None,
                 error: 'str|None' = None):
        super().__init__(parent)
        self.lineno = lineno
        self.error = error

    def run(self, result, context, run=True, templated=False):
        return IfRunner(context, run, templated).run(self, result.body.create_if())

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


class TryBranch(model.TryBranch, WithSource):
    body_class = Body
    __slots__ = ['lineno']

    def __init__(self, type: str = BodyItem.TRY,
                 patterns: Sequence[str] = (),
                 pattern_type: 'str|None' = None,
                 assign: 'str|None' = None,
                 parent: BodyItemParent = None,
                 lineno: 'int|None' = None):
        super().__init__(type, patterns, pattern_type, assign, parent)
        self.lineno = lineno

    @classmethod
    def from_dict(cls, data: DataDict) -> 'TryBranch':
        # RF 6.1 compatibility.
        if 'variable' in data:
            data['assign'] = data.pop('variable')
        return super().from_dict(data)

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        return data


@Body.register
class Try(model.Try, WithSource):
    branch_class = TryBranch
    branches_class = Branches[branch_class]
    __slots__ = ['lineno', 'error']

    def __init__(self, parent: BodyItemParent = None,
                 lineno: 'int|None' = None,
                 error: 'str|None' = None):
        super().__init__(parent)
        self.lineno = lineno
        self.error = error

    def run(self, result, context, run=True, templated=False):
        return TryRunner(context, run, templated).run(self, result.body.create_try())

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


@Body.register
class Var(model.Var, WithSource):
    __slots__ = ['lineno', 'error']

    def __init__(self, name: str = '',
                 value: 'str|Sequence[str]' = (),
                 scope: 'str|None' = None,
                 separator: 'str|None' = None,
                 parent: BodyItemParent = None,
                 lineno: 'int|None' = None,
                 error: 'str|None' = None):
        super().__init__(name, value, scope, separator, parent)
        self.lineno = lineno
        self.error = error

    def run(self, result, context, run=True, templated=False):
        result = result.body.create_var(self.name, self.value, self.scope, self.separator)
        with StatusReporter(self, result, context, run):
            if self.error and run:
                raise DataError(self.error, syntax=True)
            if not run or context.dry_run:
                return
            scope, config = self._get_scope(context.variables)
            set_variable = getattr(context.variables, f'set_{scope}')
            try:
                name, value = self._resolve_name_and_value(context.variables)
                set_variable(name, value, **config)
                context.info(format_assign_message(name, value))
            except DataError as err:
                raise VariableError(f"Setting variable '{self.name}' failed: {err}")

    def _get_scope(self, variables):
        if not self.scope:
            return 'local', {}
        try:
            scope = variables.replace_string(self.scope)
            if scope.upper() == 'TASK':
                return 'test', {}
            if scope.upper() == 'SUITES':
                return 'suite', {'children': True}
            if scope.upper() in ('LOCAL', 'TEST', 'SUITE', 'GLOBAL'):
                return scope.lower(), {}
            raise DataError(f"Value '{scope}' is not accepted. Valid values are "
                            f"'LOCAL', 'TEST', 'TASK', 'SUITE', 'SUITES' and 'GLOBAL'.")
        except DataError as err:
            raise DataError(f"Invalid VAR scope: {err}")

    def _resolve_name_and_value(self, variables):
        name = self.name[:2] + variables.replace_string(self.name[2:-1]) + '}'
        value = VariableResolver.from_variable(self).resolve(variables)
        return name, value

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


@Body.register
class Return(model.Return, WithSource):
    __slots__ = ['lineno', 'error']

    def __init__(self, values: Sequence[str] = (),
                 parent: BodyItemParent = None,
                 lineno: 'int|None' = None,
                 error: 'str|None' = None):
        super().__init__(values, parent)
        self.lineno = lineno
        self.error = error

    def run(self, result, context, run=True, templated=False):
        result = result.body.create_return(self.values)
        with StatusReporter(self, result, context, run):
            if run:
                if self.error:
                    raise DataError(self.error, syntax=True)
                if not context.dry_run:
                    raise ReturnFromKeyword(self.values)

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


@Body.register
class Continue(model.Continue, WithSource):
    __slots__ = ['lineno', 'error']

    def __init__(self, parent: BodyItemParent = None,
                 lineno: 'int|None' = None,
                 error: 'str|None' = None):
        super().__init__(parent)
        self.lineno = lineno
        self.error = error

    def run(self, result, context, run=True, templated=False):
        result = result.body.create_continue()
        with StatusReporter(self, result, context, run):
            if run:
                if self.error:
                    raise DataError(self.error, syntax=True)
                if not context.dry_run:
                    raise ContinueLoop()

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


@Body.register
class Break(model.Break, WithSource):
    __slots__ = ['lineno', 'error']

    def __init__(self, parent: BodyItemParent = None,
                 lineno: 'int|None' = None,
                 error: 'str|None' = None):
        super().__init__(parent)
        self.lineno = lineno
        self.error = error

    def run(self, result, context, run=True, templated=False):
        result = result.body.create_break()
        with StatusReporter(self, result, context, run):
            if run:
                if self.error:
                    raise DataError(self.error, syntax=True)
                if not context.dry_run:
                    raise BreakLoop()

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data


@Body.register
class Error(model.Error, WithSource):
    __slots__ = ['lineno', 'error']

    def __init__(self, values: Sequence[str] = (),
                 parent: BodyItemParent = None,
                 lineno: 'int|None' = None,
                 error: str = ''):
        super().__init__(values, parent)
        self.lineno = lineno
        self.error = error

    def run(self, result, context, run=True, templated=False):
        result = result.body.create_error(self.values)
        with StatusReporter(self, result, context, run):
            if run:
                raise DataError(self.error)

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.lineno:
            data['lineno'] = self.lineno
        data['error'] = self.error
        return data


class TestCase(model.TestCase[Keyword]):
    """Represents a single executable test case.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['template', 'error']
    body_class = Body        #: Internal usage only.
    fixture_class = Keyword  #: Internal usage only.

    def __init__(self, name: str = '',
                 doc: str = '',
                 tags: Sequence[str] = (),
                 timeout: 'str|None' = None,
                 lineno: 'int|None' = None,
                 parent: 'TestSuite|None' = None,
                 template: 'str|None' = None,
                 error: 'str|None' = None):
        super().__init__(name, doc, tags, timeout, lineno, parent)
        #: Name of the keyword that has been used as a template when building the test.
        # ``None`` if template is not used.
        self.template = template
        self.error = error

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        if self.template:
            data['template'] = self.template
        if self.error:
            data['error'] = self.error
        return data

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Test body as a :class:`~robot.running.Body` object."""
        return self.body_class(self, body)


class TestSuite(model.TestSuite[Keyword, TestCase]):
    """Represents a single executable test suite.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = []
    test_class = TestCase    #: Internal usage only.
    fixture_class = Keyword  #: Internal usage only.

    def __init__(self, name: str = '',
                 doc: str = '',
                 metadata: 'Mapping[str, str]|None' = None,
                 source: 'Path|str|None' = None,
                 rpa: 'bool|None' = False,
                 parent: 'TestSuite|None' = None):
        super().__init__(name, doc, metadata, source, rpa, parent)
        #: :class:`ResourceFile` instance containing imports, variables and
        #: keywords the suite owns. When data is parsed from the file system,
        #: this data comes from the same test case file that creates the suite.
        self.resource = None

    @setter
    def resource(self, resource: 'ResourceFile|dict|None') -> 'ResourceFile':
        from .resourcemodel import ResourceFile

        if resource is None:
            resource = ResourceFile()
        if isinstance(resource, dict):
            resource = ResourceFile.from_dict(resource)
        resource.owner = self
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

    def configure(self, randomize_suites: bool = False, randomize_tests: bool = False,
                  randomize_seed: 'int|None' = None, **options):
        """A shortcut to configure a suite using one method call.

        Can only be used with the root test suite.

        :param randomize_xxx: Passed to :meth:`randomize`.
        :param options: Passed to
            :class:`~robot.model.configurer.SuiteConfigurer` that will then
            set suite attributes, call :meth:`filter`, etc. as needed.

        Example::

            suite.configure(include_tags=['smoke'],
                            doc='Smoke test results.')

        Not to be confused with :meth:`config` method that suites, tests,
        and keywords have to make it possible to set multiple attributes in
        one call.
        """
        super().configure(**options)
        self.randomize(randomize_suites, randomize_tests, randomize_seed)

    def randomize(self, suites: bool = True, tests: bool = True,
                  seed: 'int|None' = None):
        """Randomizes the order of suites and/or tests, recursively.

        :param suites: Boolean controlling should suites be randomized.
        :param tests: Boolean controlling should tests be randomized.
        :param seed: Random seed. Can be given if previous random order needs
            to be re-created. Seed value is always shown in logs and reports.
        """
        self.visit(Randomizer(suites, tests, seed))

    @setter
    def suites(self, suites: 'Sequence[TestSuite|DataDict]') -> TestSuites['TestSuite']:
        return TestSuites['TestSuite'](self.__class__, self, suites)

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

        Additionally, listener option allows passing object directly instead of
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

    def to_dict(self) -> DataDict:
        data = super().to_dict()
        data['resource'] = self.resource.to_dict()
        return data
