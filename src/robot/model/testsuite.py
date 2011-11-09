#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

from robot import utils

from metadata import Metadata
from testcase import TestCase
from keyword import Keyword, Keywords
from itemlist import ItemList
from critical import Critical
from tagsetter import TagSetter
from filter import Filter
from modelobject import ModelObject


class TestSuite(ModelObject):
    __slots__ = ['parent', 'source', '_name', 'doc', '_critical']
    test_class = TestCase
    keyword_class = Keyword

    def __init__(self, source='', name='', doc='', metadata=None):
        self.parent = None
        self.source = source
        self.name = name
        self.doc = doc
        self.metadata = metadata
        self.suites = []
        self.tests = []
        self.keywords = []
        self._critical = None

    def _get_name(self):
        return self._name or ' & '.join(s.name for s in self.suites)
    def _set_name(self, name):
        self._name = name
    name = property(_get_name, _set_name)

    def set_criticality(self, critical_tags=None, non_critical_tags=None):
        # TODO: should settings criticality be prevented for sub suites?
        self._critical = Critical(critical_tags, non_critical_tags)

    @property
    def critical(self):
        if self._critical:
            return self._critical
        if self.parent:
            return self.parent.critical
        if self._critical is None:
            self._critical = Critical()
        return self._critical

    @utils.setter
    def metadata(self, metadata):
        return Metadata(metadata)

    @utils.setter
    def suites(self, suites):
        return ItemList(self.__class__, suites, parent=self)

    @utils.setter
    def tests(self, tests):
        return ItemList(self.test_class, tests, parent=self)

    @utils.setter
    def keywords(self, keywords):
        return Keywords(self.keyword_class, keywords, parent=self)

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

    def set_tags(self, add=None, remove=None):
        self.visit(TagSetter(add, remove))

    def filter(self, included_suites=None, included_tests=None,
               included_tags=None, excluded_tags=None):
        self.visit(Filter(included_suites, included_tests,
                          included_tags, excluded_tags))

    def visit(self, visitor):
        visitor.visit_suite(self)
