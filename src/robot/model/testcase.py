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

from robot.utils import py3to2, setter

from .body import Body
from .fixture import create_fixture
from .itemlist import ItemList
from .keyword import Keyword, Keywords
from .modelobject import ModelObject
from .tags import Tags


@py3to2
class TestCase(ModelObject):
    """Base model for a single test case.

    Extended by :class:`robot.running.model.TestCase` and
    :class:`robot.result.model.TestCase`.
    """
    body_class = Body
    fixture_class = Keyword
    repr_args = ('name',)
    __slots__ = ['parent', 'name', 'doc', 'timeout']

    def __init__(self, name='', doc='', tags=None, timeout=None, parent=None):
        self.name = name
        self.doc = doc
        self.timeout = timeout
        self.tags = tags
        self.parent = parent
        self.body = None
        self.setup = None
        self.teardown = None

    @setter
    def body(self, body):
        """Test case body as a :class:`~.Body` object."""
        return self.body_class(self, body)

    @setter
    def tags(self, tags):
        """Test tags as a :class:`~.model.tags.Tags` object."""
        return Tags(tags)

    @setter
    def setup(self, setup):
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
        return create_fixture(setup, self, Keyword.SETUP)

    @setter
    def teardown(self, teardown):
        """Test teardown as a :class:`~.model.keyword.Keyword` object.

        See :attr:`setup` for more information.
        """
        return create_fixture(teardown, self, Keyword.TEARDOWN)

    @property
    def keywords(self):
        """Deprecated since Robot Framework 4.0

        Use :attr:`body`, :attr:`setup` or :attr:`teardown` instead.
        """
        keywords = [self.setup] + list(self.body) + [self.teardown]
        return Keywords(self, [kw for kw in keywords if kw])

    @keywords.setter
    def keywords(self, keywords):
        Keywords.raise_deprecation_error()

    @property
    def id(self):
        """Test case id in format like ``s1-t3``.

        See :attr:`TestSuite.id <robot.model.testsuite.TestSuite.id>` for
        more information.
        """
        if not self.parent:
            return 't1'
        return '%s-t%d' % (self.parent.id, self.parent.tests.index(self)+1)

    @property
    def longname(self):
        """Test name prefixed with the long name of the parent suite."""
        if not self.parent:
            return self.name
        return '%s.%s' % (self.parent.longname, self.name)

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def visit(self, visitor):
        """:mod:`Visitor interface <robot.model.visitor>` entry-point."""
        visitor.visit_test(self)

    def __str__(self):
        return self.name


class TestCases(ItemList):
    __slots__ = []

    def __init__(self, test_class=TestCase, parent=None, tests=None):
        ItemList.__init__(self, test_class, {'parent': parent}, tests)

    def _check_type_and_set_attrs(self, *tests):
        tests = ItemList._check_type_and_set_attrs(self, *tests)
        for test in tests:
            for visitor in test.parent._visitors:
                test.visit(visitor)
        return tests
