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

from robot.utils import setter

from .configurer import SuiteConfigurer
from .filter import Filter, EmptySuiteRemover
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
    __slots__ = ['parent', 'source', '_name', 'doc', '_my_visitors']
    test_class = TestCase    #: Internal usage only.
    keyword_class = Keyword  #: Internal usage only.

    def __init__(self, name='', doc='', metadata=None, source=None):
        self.parent = None  #: Parent suite. ``None`` with the root suite.
        self._name = name
        self.doc = doc  #: Test suite documentation.
        self.metadata = metadata
        self.source = source  #: Path to the source file or directory.
        self.suites = None
        self.tests = None
        self.keywords = None
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

    @setter
    def keywords(self, keywords):
        """Suite setup and teardown as a :class:`~.Keywords` object."""
        return Keywords(self.keyword_class, self, keywords)

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

        :param options: Passed to
            :class:`~robot.model.configurer.SuiteConfigurer` that will then
            set suite attributes, call :meth:`filter`, etc. as needed.
        """
        self.visit(SuiteConfigurer(**options))

    def remove_empty_suites(self):
        """Removes all child suites not containing any tests, recursively."""
        self.visit(EmptySuiteRemover())

    def visit(self, visitor):
        """:mod:`Visitor interface <robot.model.visitor>` entry-point."""
        visitor.visit_suite(self)


class TestSuites(ItemList):
    __slots__ = []

    def __init__(self, suite_class=TestSuite, parent=None, suites=None):
        ItemList.__init__(self, suite_class, {'parent': parent}, suites)
