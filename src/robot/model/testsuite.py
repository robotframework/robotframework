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

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Generic, Iterator, Sequence, Type, TypeVar

from robot.errors import DataError
from robot.utils import seq2str, setter

from .configurer import SuiteConfigurer
from .filter import Filter, EmptySuiteRemover
from .fixture import create_fixture
from .itemlist import ItemList
from .keyword import Keyword
from .metadata import Metadata
from .modelobject import DataDict, ModelObject
from .tagsetter import TagSetter
from .testcase import TestCase, TestCases
from .visitor import SuiteVisitor

TS = TypeVar('TS', bound='TestSuite')
KW = TypeVar('KW', bound=Keyword, covariant=True)
TC = TypeVar('TC', bound=TestCase, covariant=True)


class TestSuite(ModelObject, Generic[KW, TC]):
    """Base model for single suite.

    Extended by :class:`robot.running.model.TestSuite` and
    :class:`robot.result.model.TestSuite`.
    """
    # FIXME: Type Ignore declarations: Typevars only accept subclasses of the bound class
    # assigning `Type[KW]` to `Keyword` results in an error. In RF 7 the class should be
    # made impossible to instantiate directly, and the assignments can be replaced with
    # KnownAtRuntime
    fixture_class: Type[KW] = Keyword  # type: ignore
    test_class: Type[TC] = TestCase  # type: ignore

    repr_args = ('name',)
    __slots__ = ['parent', '_name', 'doc', '_setup', '_teardown', 'rpa', '_my_visitors']

    def __init__(self, name: str = '',
                 doc: str = '',
                 metadata: 'Mapping[str, str]|None' = None,
                 source: 'Path|str|None' = None,
                 rpa: 'bool|None' = False,
                 parent: 'TestSuite[KW, TC]|None' = None):
        self._name = name
        self.doc = doc
        self.metadata = metadata
        self.source = source
        self.parent = parent
        self.rpa = rpa
        self.suites = []
        self.tests = []
        self._setup: 'KW|None' = None
        self._teardown: 'KW|None' = None
        self._my_visitors: 'list[SuiteVisitor]' = []

    @staticmethod
    def name_from_source(source: 'Path|str|None', extension: Sequence[str] = ()) -> str:
        """Create suite name based on the given ``source``.

        This method is used by Robot Framework itself when it builds suites.
        External parsers and other tools that want to produce suites with
        names matching names created by Robot Framework can use this method as
        well. This method is also used if :attr:`name` is not set and someone
        accesses it.

        The algorithm is as follows:

        - If the source is ``None`` or empty, return an empty string.
        - Get the base name of the source. Read more below.
        - Remove possible prefix separated with ``__``.
        - Convert underscores to spaces.
        - If the name is all lower case, title case it.

        The base name of files is got by calling `Path.stem`__ that drops
        the file extension. It typically works fine, but gives wrong result
        if the extension has multiple parts like in ``tests.robot.zip``.
        That problem can be avoided by giving valid file extension or extensions
        as the optional ``extension`` argument.

        Examples::

            TestSuite.name_from_source(source)
            TestSuite.name_from_source(source, extension='.robot.zip')
            TestSuite.name_from_source(source, ('.robot', '.robot.zip'))

        __ https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.stem
        """
        if not source:
            return ''
        if not isinstance(source, Path):
            source = Path(source)
        name = TestSuite._get_base_name(source, extension)
        if '__' in name:
            name = name.split('__', 1)[1] or name
        name = name.replace('_', ' ').strip()
        return name.title() if name.islower() else name

    @staticmethod
    def _get_base_name(path: Path, extensions: Sequence[str]) -> str:
        if path.is_dir():
            return path.name
        if not extensions:
            return path.stem
        if isinstance(extensions, str):
            extensions = [extensions]
        for ext in extensions:
            ext = '.' + ext.lower().lstrip('.')
            if path.name.lower().endswith(ext):
                return path.name[:-len(ext)]
        raise ValueError(f"File '{path}' does not have extension "
                         f"{seq2str(extensions, lastsep=' or ')}.")

    @property
    def _visitors(self) -> 'list[SuiteVisitor]':
        parent_visitors = self.parent._visitors if self.parent else []
        return self._my_visitors + parent_visitors

    @property
    def name(self) -> str:
        """Suite name.

        If name is not set, it is constructed from source. If source is not set,
        name is constructed from child suite names by concatenating them with
        `` & ``. If there are no child suites, name is an empty string.
        """
        return (self._name
                or self.name_from_source(self.source)
                or ' & '.join(s.name for s in self.suites))

    @name.setter
    def name(self, name: str):
        self._name = name

    @setter
    def source(self, source: 'Path|str|None') -> 'Path|None':
        return source if isinstance(source, (Path, type(None))) else Path(source)

    def adjust_source(self, relative_to: 'Path|str|None' = None,
                      root: 'Path|str|None' = None):
        """Adjust suite source and child suite sources, recursively.

        :param relative_to: Make suite source relative to the given path. Calls
            `pathlib.Path.relative_to()`__ internally. Raises ``ValueError``
            if creating a relative path is not possible.
        :param root: Make given path a new root directory for the source. Raises
            ``ValueError`` if suite source is absolute.

        Adjusting the source is especially useful when moving data around as JSON::

            from robot.api import TestSuite

            # Create a suite, adjust source and convert to JSON.
            suite = TestSuite.from_file_system('/path/to/data')
            suite.adjust_source(relative_to='/path/to')
            suite.to_json('data.rbt')

            # Recreate suite elsewhere and adjust source accordingly.
            suite = TestSuite.from_json('data.rbt')
            suite.adjust_source(root='/new/path/to')

        New in Robot Framework 6.1.

        __ https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.relative_to
        """
        if not self.source:
            raise ValueError('Suite has no source.')
        if relative_to:
            self.source = self.source.relative_to(relative_to)
        if root:
            if self.source.is_absolute():
                raise ValueError(f"Cannot set root for absolute source '{self.source}'.")
            self.source = root / self.source
        for suite in self.suites:
            suite.adjust_source(relative_to, root)

    @property
    def full_name(self) -> str:
        """Suite name prefixed with the full name of the possible parent suite.

        Just :attr:`name` of the suite if it has no :attr:`parent`.
        """
        if not self.parent:
            return self.name
        return f'{self.parent.full_name}.{self.name}'

    @property
    def longname(self) -> str:
        """Deprecated since Robot Framework 7.0. Use :attr:`full_name` instead."""
        return self.full_name

    @setter
    def metadata(self, metadata: 'Mapping[str, str]|None') -> Metadata:
        """Free suite metadata as a :class:`~.metadata.Metadata` object."""
        return Metadata(metadata)

    def validate_execution_mode(self) -> 'bool|None':
        """Validate that suite execution mode is set consistently.

        Raise an exception if the execution mode is not set (i.e. the :attr:`rpa`
        attribute is ``None``) and child suites have conflicting execution modes.

        The execution mode is returned. New in RF 6.1.1.
        """
        if self.rpa is None:
            rpa = name = None
            for suite in self.suites:
                suite.validate_execution_mode()
                if rpa is None:
                    rpa = suite.rpa
                    name = suite.full_name
                elif rpa is not suite.rpa:
                    mode1, mode2 = ('tasks', 'tests') if rpa else ('tests', 'tasks')
                    raise DataError(
                        f"Conflicting execution modes: Suite '{name}' has {mode1} but "
                        f"suite '{suite.full_name}' has {mode2}. Resolve the conflict "
                        f"or use '--rpa' or '--norpa' options to set the execution "
                        f"mode explicitly."
                    )
            self.rpa = rpa
        return self.rpa

    @setter
    def suites(self, suites: 'Sequence[TestSuite|DataDict]') -> 'TestSuites[TestSuite[KW, TC]]':
        return TestSuites['TestSuite'](self.__class__, self, suites)

    @setter
    def tests(self, tests: 'Sequence[TC|DataDict]') -> TestCases[TC]:
        return TestCases[TC](self.test_class, self, tests)

    @property
    def setup(self) -> KW:
        """Suite setup.

        This attribute is a ``Keyword`` object also when a suite has no setup
        but in that case its truth value is ``False``. The preferred way to
        check does a suite have a setup is using :attr:`has_setup`.

        Setup can be modified by setting attributes directly::

            suite.setup.name = 'Example'
            suite.setup.args = ('First', 'Second')

        Alternatively the :meth:`config` method can be used to set multiple
        attributes in one call::

            suite.setup.config(name='Example', args=('First', 'Second'))

        The easiest way to reset the whole setup is setting it to ``None``.
        It will automatically recreate the underlying ``Keyword`` object::

            suite.setup = None

        New in Robot Framework 4.0. Earlier setup was accessed like
        ``suite.keywords.setup``.
        """
        if self._setup is None:
            self._setup = create_fixture(self.fixture_class, None, self, Keyword.SETUP)
        return self._setup

    @setup.setter
    def setup(self, setup: 'KW|DataDict|None'):
        self._setup = create_fixture(self.fixture_class, setup, self, Keyword.SETUP)

    @property
    def has_setup(self) -> bool:
        """Check does a suite have a setup without creating a setup object.

        A difference between using ``if suite.has_setup:`` and ``if suite.setup:``
        is that accessing the :attr:`setup` attribute creates a :class:`Keyword`
        object representing the setup even when the suite actually does not have
        one. This typically does not matter, but with bigger suite structures
        it can have some effect on memory usage.

        New in Robot Framework 5.0.
        """
        return bool(self._setup)

    @property
    def teardown(self) -> KW:
        """Suite teardown.

        See :attr:`setup` for more information.
        """
        if self._teardown is None:
            self._teardown = create_fixture(self.fixture_class, None, self, Keyword.TEARDOWN)
        return self._teardown

    @teardown.setter
    def teardown(self, teardown: 'KW|DataDict|None'):
        self._teardown = create_fixture(self.fixture_class, teardown, self, Keyword.TEARDOWN)

    @property
    def has_teardown(self) -> bool:
        """Check does a suite have a teardown without creating a teardown object.

        See :attr:`has_setup` for more information.

        New in Robot Framework 5.0.
        """
        return bool(self._teardown)

    @property
    def id(self) -> str:
        """An automatically generated unique id.

        The root suite has id ``s1``, its child suites have ids ``s1-s1``,
        ``s1-s2``, ..., their child suites get ids ``s1-s1-s1``, ``s1-s1-s2``,
        ..., ``s1-s2-s1``, ..., and so on.

        The first test in a suite has an id like ``s1-t1``, the second has an
        id ``s1-t2``, and so on. Similarly, keywords in suites (setup/teardown)
        and in tests get ids like ``s1-k1``, ``s1-t1-k1``, and ``s1-s4-t2-k5``.
        """
        if not self.parent:
            return 's1'
        suites = self.parent.suites
        index = suites.index(self) if self in suites else len(suites)
        return f'{self.parent.id}-s{index + 1}'

    @property
    def all_tests(self) -> Iterator[TestCase]:
        """Yields all tests this suite and its child suites contain.

        New in Robot Framework 6.1.
        """
        yield from self.tests
        for suite in self.suites:
            yield from suite.all_tests

    @property
    def test_count(self) -> int:
        """Total number of the tests in this suite and in its child suites."""
        # This is considerably faster than `return len(list(self.all_tests))`.
        return len(self.tests) + sum(suite.test_count for suite in self.suites)

    @property
    def has_tests(self) -> bool:
        return bool(self.tests) or any(s.has_tests for s in self.suites)

    def set_tags(self, add: Sequence[str] = (), remove: Sequence[str] = (),
                 persist: bool = False):
        """Add and/or remove specified tags to the tests in this suite.

        :param add: Tags to add as a list or, if adding only one,
            as a single string.
        :param remove: Tags to remove as a list or as a single string.
            Can be given as patterns where ``*`` and ``?`` work as wildcards.
        :param persist: Add/remove specified tags also to new tests added
            to this suite in the future.
        """
        setter = TagSetter(add, remove)
        self.visit(setter)
        if persist:
            self._my_visitors.append(setter)

    def filter(self, included_suites: 'Sequence[str]|None' = None,
               included_tests: 'Sequence[str]|None' = None,
               included_tags: 'Sequence[str]|None' = None,
               excluded_tags: 'Sequence[str]|None' = None):
        """Select test cases and remove others from this suite.

        Parameters have the same semantics as ``--suite``, ``--test``,
        ``--include``, and ``--exclude`` command line options. All of them
        can be given as a list of strings, or when selecting only one, as
        a single string.

        Child suites that contain no tests after filtering are automatically
        removed.

        Example::

            suite.filter(included_tests=['Test 1', '* Example'],
                         included_tags='priority-1')
        """
        self.visit(Filter(included_suites, included_tests,
                          included_tags, excluded_tags))

    def configure(self, **options):
        """A shortcut to configure a suite using one method call.

        Can only be used with the root test suite.

        :param options: Passed to
            :class:`~robot.model.configurer.SuiteConfigurer` that will then
            set suite attributes, call :meth:`filter`, etc. as needed.

        Not to be confused with :meth:`config` method that suites, tests,
        and keywords have to make it possible to set multiple attributes in
        one call.
        """
        if self.parent is not None:
            raise ValueError("'TestSuite.configure()' can only be used with "
                             "the root test suite.")
        if options:
            self.visit(SuiteConfigurer(**options))

    def remove_empty_suites(self, preserve_direct_children: bool = False):
        """Removes all child suites not containing any tests, recursively."""
        self.visit(EmptySuiteRemover(preserve_direct_children))

    def visit(self, visitor: SuiteVisitor):
        """:mod:`Visitor interface <robot.model.visitor>` entry-point."""
        visitor.visit_suite(self)

    def to_dict(self) -> 'dict[str, Any]':
        data: 'dict[str, Any]' = {'name': self.name}
        if self.doc:
            data['doc'] = self.doc
        if self.metadata:
            data['metadata'] = dict(self.metadata)
        if self.source:
            data['source'] = str(self.source)
        if self.rpa:
            data['rpa'] = self.rpa
        if self.has_setup:
            data['setup'] = self.setup.to_dict()
        if self.has_teardown:
            data['teardown'] = self.teardown.to_dict()
        if self.tests:
            data['tests'] = self.tests.to_dicts()
        if self.suites:
            data['suites'] = self.suites.to_dicts()
        return data


class TestSuites(ItemList[TS]):
    __slots__ = []

    def __init__(self, suite_class: Type[TS] = TestSuite,
                 parent: 'TS|None' = None,
                 suites: 'Sequence[TS|DataDict]' = ()):
        super().__init__(suite_class, {'parent': parent}, suites)
