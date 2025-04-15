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

from pathlib import Path
from typing import Any, Generic, Sequence, Type, TYPE_CHECKING, TypeVar

from robot.utils import setter

from .body import Body, BodyItem
from .fixture import create_fixture
from .itemlist import ItemList
from .keyword import Keyword
from .modelobject import DataDict, ModelObject
from .tags import Tags

if TYPE_CHECKING:
    from .testsuite import TestSuite
    from .visitor import SuiteVisitor


TC = TypeVar('TC', bound='TestCase')
KW = TypeVar('KW', bound='Keyword', covariant=True)


class TestCase(ModelObject, Generic[KW]):
    """Base model for a single test case.

    Extended by :class:`robot.running.model.TestCase` and
    :class:`robot.result.model.TestCase`.
    """
    type = 'TEST'
    body_class = Body
    # See model.TestSuite on removing the type ignore directive
    fixture_class: Type[KW] = Keyword    # type: ignore
    repr_args = ('name',)
    __slots__ = ['parent', 'name', 'doc', 'timeout', 'lineno', '_setup', '_teardown']

    def __init__(self, name: str = '',
                 doc: str = '',
                 tags: 'Tags|Sequence[str]' = (),
                 timeout: 'str|None' = None,
                 lineno: 'int|None' = None,
                 parent: 'TestSuite[KW, TestCase[KW]]|None' = None):
        self.name = name
        self.doc = doc
        self.tags = tags
        self.timeout = timeout
        self.lineno = lineno
        self.parent = parent
        self.body = []
        self._setup: 'KW|None' = None
        self._teardown: 'KW|None' = None

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Test body as a :class:`~robot.model.body.Body` object."""
        return self.body_class(self, body)

    @setter
    def tags(self, tags: 'Tags|Sequence[str]') -> Tags:
        """Test tags as a :class:`~.model.tags.Tags` object."""
        return Tags(tags)

    @property
    def setup(self) -> KW:
        """Test setup as a :class:`~.model.keyword.Keyword` object.

        This attribute is a ``Keyword`` object also when a test has no setup
        but in that case its truth value is ``False``.

        Setup can be modified by setting attributes directly::

            test.setup.name = 'Example'
            test.setup.args = ('First', 'Second')

        Alternatively the :meth:`config` method can be used to set multiple
        attributes in one call::

            test.setup.config(name='Example', args=('First', 'Second'))

        The easiest way to reset the whole setup is setting it to ``None``.
        It will automatically recreate the underlying ``Keyword`` object::

            test.setup = None

        New in Robot Framework 4.0. Earlier setup was accessed like
        ``test.keywords.setup``.
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

        A difference between using ``if test.has_setup:`` and ``if test.setup:``
        is that accessing the :attr:`setup` attribute creates a :class:`Keyword`
        object representing the setup even when the test actually does not have
        one. This typically does not matter, but with bigger suite structures
        containing a huge about of tests it can have an effect on memory usage.

        New in Robot Framework 5.0.
        """
        return bool(self._setup)

    @property
    def teardown(self) -> KW:
        """Test teardown as a :class:`~.model.keyword.Keyword` object.

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
        """Check does a test have a teardown without creating a teardown object.

        See :attr:`has_setup` for more information.

        New in Robot Framework 5.0.
        """
        return bool(self._teardown)

    @property
    def id(self) -> str:
        """Test case id in format like ``s1-t3``.

        See :attr:`TestSuite.id <robot.model.testsuite.TestSuite.id>` for
        more information.
        """
        if not self.parent:
            return 't1'
        tests = self.parent.tests
        index = tests.index(self) if self in tests else len(tests)
        return f'{self.parent.id}-t{index + 1}'

    @property
    def full_name(self) -> str:
        """Test name prefixed with the full name of the parent suite."""
        if not self.parent:
            return self.name
        return f'{self.parent.full_name}.{self.name}'

    @property
    def longname(self) -> str:
        """Deprecated since Robot Framework 7.0. Use :attr:`full_name` instead."""
        return self.full_name

    @property
    def source(self) -> 'Path|None':
        return self.parent.source if self.parent is not None else None

    def visit(self, visitor: 'SuiteVisitor'):
        """:mod:`Visitor interface <robot.model.visitor>` entry-point."""
        visitor.visit_test(self)

    def to_dict(self) -> 'dict[str, Any]':
        data: 'dict[str, Any]' = {'name': self.name}
        if self.doc:
            data['doc'] = self.doc
        if self.tags:
            data['tags'] = tuple(self.tags)
        if self.timeout:
            data['timeout'] = self.timeout
        if self.lineno:
            data['lineno'] = self.lineno
        if self.has_setup:
            data['setup'] = self.setup.to_dict()
        if self.has_teardown:
            data['teardown'] = self.teardown.to_dict()
        data['body'] = self.body.to_dicts()
        return data


class TestCases(ItemList[TC]):
    __slots__ = []

    def __init__(self, test_class: Type[TC] = TestCase,
                 parent: 'TestSuite|None' = None,
                 tests: 'Sequence[TC|DataDict]' = ()):
        super().__init__(test_class, {'parent': parent}, tests)

    def _check_type_and_set_attrs(self, test):
        test = super()._check_type_and_set_attrs(test)
        if test.parent:
            for visitor in test.parent._visitors:
                test.visit(visitor)
        return test
