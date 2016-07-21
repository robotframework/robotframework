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

from .itemlist import ItemList
from .keyword import Keyword, Keywords
from .modelobject import ModelObject
from .tags import Tags


class TestCase(ModelObject):
    """Base model for a single test case.

    Extended by :class:`robot.running.model.TestCase` and
    :class:`robot.result.model.TestCase`.
    """
    __slots__ = ['parent', 'name', 'doc', 'timeout']
    keyword_class = Keyword  #: Internal usage only

    def __init__(self, name='', doc='', tags=None, timeout=None):
        self.parent = None      #: Parent suite.
        self.name = name        #: Test case name.
        self.doc = doc          #: Test case documentation.
        self.timeout = timeout  #: Test case timeout.
        self.tags = tags
        self.keywords = None

    @setter
    def tags(self, tags):
        """Test tags as a :class:`~.model.tags.Tags` object."""
        return Tags(tags)

    @setter
    def keywords(self, keywords):
        """Keywords as a :class:`~.Keywords` object.

        Contains also possible setup and teardown keywords.
        """
        return Keywords(self.keyword_class, self, keywords)

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

    def visit(self, visitor):
        """:mod:`Visitor interface <robot.model.visitor>` entry-point."""
        visitor.visit_test(self)


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
