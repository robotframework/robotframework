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

from .itemlist import ItemList
from .keyword import Keyword, Keywords
from .modelobject import ModelObject
from .tags import Tags


class TestCase(ModelObject):
    __slots__ = ['parent', 'name', 'doc', 'timeout']
    keyword_class = Keyword

    def __init__(self, name='', doc='', tags=None, timeout=''):
        self.parent = None
        self.name = name
        self.doc = doc
        self.tags = tags
        self.timeout = timeout
        self.keywords = []

    @setter
    def tags(self, tags):
        return Tags(tags)

    @setter
    def keywords(self, keywords):
        return Keywords(self.keyword_class, self, keywords)

    @property
    def id(self):
        if not self.parent:
            return 't1'
        return '%s-t%d' % (self.parent.id, self.parent.tests.index(self)+1)

    @property
    def longname(self):
        if not self.parent:
            return self.name
        return '%s.%s' % (self.parent.longname, self.name)

    @property
    def critical(self):
        if not self.parent:
            return True
        return self.parent.criticality.test_is_critical(self)

    def visit(self, visitor):
        visitor.visit_test(self)


class TestCases(ItemList):
    __slots__ = []

    def __init__(self, test_class=TestCase, parent=None, tests=None):
        ItemList.__init__(self, test_class, {'parent': parent}, tests)
