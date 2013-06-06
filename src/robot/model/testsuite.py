#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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
from .criticality import Criticality
from .filter import Filter, EmptySuiteRemover
from .itemlist import ItemList
from .keyword import Keyword, Keywords
from .metadata import Metadata
from .modelobject import ModelObject
from .tagsetter import TagSetter
from .testcase import TestCase, TestCases


class TestSuite(ModelObject):
    __slots__ = ['parent', 'source', '_name', 'doc', '_my_visitors']
    test_class = TestCase
    keyword_class = Keyword

    def __init__(self, name='', doc='', metadata=None, source=None):
        self.parent = None
        self.name = name
        self.doc = doc
        self.metadata = metadata
        self.source = source
        self.suites = []
        self.tests = []
        self.keywords = []
        self._my_visitors = []


    @property
    def _visitors(self):
        parent_visitors = self.parent._visitors if self.parent else []
        return self._my_visitors + parent_visitors

    def _get_name(self):
        return self._name or ' & '.join(s.name for s in self.suites)
    def _set_name(self, name):
        self._name = name
    name = property(_get_name, _set_name)

    @property
    def criticality(self):
        if self.parent:
            return self.parent.criticality
        return Criticality()

    @setter
    def metadata(self, metadata):
        return Metadata(metadata)

    @setter
    def suites(self, suites):
        return TestSuites(self.__class__, self, suites)

    @setter
    def tests(self, tests):
        return TestCases(self.test_class, self, tests)

    @setter
    def keywords(self, keywords):
        return Keywords(self.keyword_class, self, keywords)

    @property
    def id(self):
        if not self.parent:
            return 's1'
        return '%s-s%d' % (self.parent.id, self.parent.suites.index(self)+1)

    @property
    def longname(self):
        if not self.parent:
            return self.name
        return '%s.%s' % (self.parent.longname, self.name)

    @property
    def test_count(self):
        return len(self.tests) + sum(suite.test_count for suite in self.suites)

    def set_tags(self, add=None, remove=None, persist=False):
        setter = TagSetter(add, remove)
        self.visit(setter)
        if persist:
            self._my_visitors.append(setter)

    def filter(self, included_suites=None, included_tests=None,
               included_tags=None, excluded_tags=None):
        self.visit(Filter(included_suites, included_tests,
                          included_tags, excluded_tags))

    def configure(self, **options):
        self.visit(SuiteConfigurer(**options))

    def remove_empty_suites(self):
        self.visit(EmptySuiteRemover())

    def visit(self, visitor):
        visitor.visit_suite(self)


class TestSuites(ItemList):
    __slots__ = []

    def __init__(self, suite_class=TestSuite, parent=None, suites=None):
        ItemList.__init__(self, suite_class, {'parent': parent}, suites)
