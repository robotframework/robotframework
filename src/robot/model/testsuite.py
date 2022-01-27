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

from robot.utils import setter

from .configurer import SuiteConfigurer
from .filter import Filter, EmptySuiteRemover
from .fixture import create_fixture
from .itemlist import ItemList
from .keyword import Keyword, Keywords
from .metadata import Metadata
from .modelobject import ModelObject
from .tagsetter import TagSetter
from .testcase import TestCase, TestCases


class TestSuite(ModelObject):
    """Base model for single suite.

    Extended by :class:`robot.running.model.TestSuite` and
    :class:`robot.result.model.TestSuite`.
    """
    test_class = TestCase    #: Internal usage only.
    fixture_class = Keyword  #: Internal usage only.
    repr_args = ('name',)
    __slots__ = ['parent', 'source', '_name', 'doc', '_setup', '_teardown',  'rpa',
                 '_my_visitors']

    def __init__(self, name='', doc='', metadata=None, source=None, rpa=False,
                 parent=None):
        self._name = name
        self.doc = doc
        self.metadata = metadata
        self.source = source  #: Path to the source file or directory.
        self.parent = parent  #: Parent suite. ``None`` with the root suite.
        self.rpa = rpa        #: ``True`` when RPA mode is enabled.
        self.suites = None
        self.tests = None
        self._setup = None
        self._teardown = None
        self._my_visitors = []

    @property
    def _visitors(self):
        parent_visitors = self.parent._visitors if self.parent else []
        return self._my_visitors + parent_visitors

    @property
    def name(self):
        """Test suite name. If not set, constructed from child suite names."""
        return self._name or ' & '.join(s.name for s in self.suites)

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def longname(self):
        """Suite name prefixed with the long name of the parent suite."""
        if not self.parent:
            return self.name
        return '%s.%s' % (self.parent.longname, self.name)

    @setter
    def metadata(self, metadata):
        """Free test suite metadata as a dictionary."""
        return Metadata(metadata)

    @setter
    def suites(self, suites):
        """Child suites as a :class:`~.TestSuites` object."""
        return TestSuites(self.__class__, self, suites)

    @setter
    def tests(self, tests):
        """Tests as a :class:`~.TestCases` object."""
        return TestCases(self.test_class, self, tests)

    @property
    def setup(self):
        """Suite setup as a :class:`~.model.keyword.Keyword` object.

        This attribute is a ``Keyword`` object also when a suite has no setup
        but in that case its truth value is ``False``.

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
        if self._setup is None and self:
            self._setup = create_fixture(None, self, Keyword.SETUP)
        return self._setup

    @setup.setter
    def setup(self, setup):
        self._setup = create_fixture(setup, self, Keyword.SETUP)

    @property
    def has_setup(self):
        """Check does a suite have a setup without creating a setup object.

        A difference between using ``if suite.has_setup:`` and ``if suite.setup:``
        is that accessing the :attr:`setup` attribute creates a :class:`Keyword`
        object representing the setup even when the suite actually does not have
        one. This typically does not matter, but with bigger suite structures
        containing a huge about of suites it can have some effect on memory usage.

        New in Robot Framework 5.0.
        """

        return bool(self._setup)

    @property
    def teardown(self):
        """Suite teardown as a :class:`~.model.keyword.Keyword` object.

        See :attr:`setup` for more information.
        """
        if self._teardown is None and self:
            self._teardown = create_fixture(None, self, Keyword.TEARDOWN)
        return self._teardown

    @teardown.setter
    def teardown(self, teardown):
        self._teardown = create_fixture(teardown, self, Keyword.TEARDOWN)

    @property
    def has_teardown(self):
        """Check does a suite have a teardown without creating a teardown object.

        See :attr:`has_setup` for more information.

        New in Robot Framework 5.0.
        """
        return bool(self._teardown)

    @property
    def keywords(self):
        """Deprecated since Robot Framework 4.0

        Use :attr:`setup` or :attr:`teardown` instead.
        """
        keywords = [self.setup, self.teardown]
        return Keywords(self, [kw for kw in keywords if kw])

    @keywords.setter
    def keywords(self, keywords):
        Keywords.raise_deprecation_error()

    @property
    def id(self):
        """An automatically generated unique id.

        The root suite has id ``s1``, its child suites have ids ``s1-s1``,
        ``s1-s2``, ..., their child suites get ids ``s1-s1-s1``, ``s1-s1-s2``,
        ..., ``s1-s2-s1``, ..., and so on.

        The first test in a suite has an id like ``s1-t1``, the second has an
        id ``s1-t2``, and so on. Similarly keywords in suites (setup/teardown)
        and in tests get ids like ``s1-k1``, ``s1-t1-k1``, and ``s1-s4-t2-k5``.
        """
        if not self.parent:
            return 's1'
        return '%s-s%d' % (self.parent.id, self.parent.suites.index(self)+1)

    @property
    def test_count(self):
        """Number of the tests in this suite, recursively."""
        return len(self.tests) + sum(suite.test_count for suite in self.suites)

    @property
    def has_tests(self):
        if self.tests:
            return True
        return any(s.has_tests for s in self.suites)

    def set_tags(self, add=None, remove=None, persist=False):
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

    def filter(self, included_suites=None, included_tests=None,
               included_tags=None, excluded_tags=None):
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

    def remove_empty_suites(self, preserve_direct_children=False):
        """Removes all child suites not containing any tests, recursively."""
        self.visit(EmptySuiteRemover(preserve_direct_children))

    def visit(self, visitor):
        """:mod:`Visitor interface <robot.model.visitor>` entry-point."""
        visitor.visit_suite(self)

    def __str__(self):
        return self.name


class TestSuites(ItemList):
    __slots__ = []

    def __init__(self, suite_class=TestSuite, parent=None, suites=None):
        ItemList.__init__(self, suite_class, {'parent': parent}, suites)
