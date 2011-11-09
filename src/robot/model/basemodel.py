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

from robot.output.loggerhelper import Message as BaseMessage
from robot import utils

from robot.model import Tags, Critical
from robot.model.metadata import Metadata

#from tagsetter import TagSetter
#from filter import Filter, MessageFilter
#from configurer import SuiteConfigurer


class TestSuite(object):
    __slots__ = ['parent', 'source', '_name', 'doc', '_setter__metadata',
                 '_setter__suites', '_setter__tests', '_setter__keywords',
                 '_critical']

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
        return ItemList(TestSuite, suites, parent=self)

    @utils.setter
    def tests(self, tests):
        return ItemList(TestCase, tests, parent=self)

    @utils.setter
    def keywords(self, keywords):
        return Keywords(keywords, parent=self)

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

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('UTF-8')

    def __repr__(self):
        return repr(str(self))


class TestCase(object):
    __slots__ = ['parent', 'name', 'doc', 'timeout', '_setter__tags',
                 '_setter__keywords']

    def __init__(self, name='', doc='', tags=None, timeout=''):
        self.parent = None
        self.name = name
        self.doc = doc
        self.tags = tags
        self.timeout = timeout
        self.keywords = []

    @utils.setter
    def tags(self, tags):
        return Tags(tags)

    @utils.setter
    def keywords(self, keywords):
        return Keywords(keywords, parent=self)

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
        return 'yes' if self.parent.critical.test_is_critical(self) else 'no'

    def visit(self, visitor):
        visitor.visit_test(self)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('UTF-8')

    def __repr__(self):
        return repr(str(self))


class Keyword(object):
    __slots__ = ['parent', 'name', 'doc', 'args', 'type', 'timeout',
                 '_setter__messages', '_setter__keywords']

    def __init__(self, name='', doc='', args=None, type='kw', timeout=''):
        self.parent = None
        self.name = name
        self.doc = doc
        self.args = args or []
        self.type = type
        self.timeout = timeout
        self.messages = []
        self.keywords = []

    @utils.setter
    def keywords(self, keywords):
        return Keywords(keywords, parent=self)

    @utils.setter
    def messages(self, messages):
        return ItemList(Message, messages)

    @property
    def id(self):
        if not self.parent:
            return 'k1'
        return '%s-k%d' % (self.parent.id, self.parent.keywords.index(self)+1)

    # TODO: Is this generally needed? If yes, do we also need is_setup etc?
    @property
    def is_forloop(self):
        return self.type == 'for'

    def visit(self, visitor):
        visitor.visit_keyword(self)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('UTF-8')

    def __repr__(self):
        return repr(str(self))


# TODO: Inheritance should work other way. This should be the base.
class Message(BaseMessage):
    __slots__ = []

    def __init__(self, message='', level='INFO', html=False, timestamp=None,
                 linkable=False):
        BaseMessage.__init__(self, message, level, html, timestamp, linkable)

    def visit(self, visitor):
        visitor.visit_message(self)


class ItemList(object):
    __slots__ = ['_item_class', '_parent', '_items']

    def __init__(self, item_class, items=None, parent=None):
        # TODO: This really should accept generic **common_attrs and not
        # parent. Need to investigate why **common_attrs took so much memory.
        self._item_class = item_class
        self._parent = parent
        self._items = []
        if items:
            self.extend(items)

    def create(self, *args, **kwargs):
        self.append(self._item_class(*args, **kwargs))
        return self._items[-1]

    def append(self, item):
        self._check_type_and_set_attrs(item)
        self._items.append(item)

    def _check_type_and_set_attrs(self, item):
        if not isinstance(item, self._item_class):
            raise TypeError("Only '%s' objects accepted, got '%s'"
                            % (self._item_class.__name__, type(item).__name__))
        if self._parent:
            item.parent = self._parent

    def extend(self, items):
        for item in items:
            self._check_type_and_set_attrs(item)
        self._items.extend(items)

    def index(self, item):
        return self._items.index(item)

    def visit(self, visitor):
        for item in self:
            item.visit(visitor)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        if isinstance(index, slice):
            raise ValueError("'%s' object does not support slicing" % type(self).__name__)
        return self._items[index]

    def __len__(self):
        return len(self._items)

    def __unicode__(self):
        return u'[%s]' % ', '.join(unicode(item) for item in self)

    def __str__(self):
        return unicode(self).encode('UTF-8')


class Keywords(ItemList):
    __slots__ = []

    def __init__(self, items=None, parent=None):
        ItemList.__init__(self, Keyword, items, parent)

    @property
    def setup(self):
        return self[0] if (self and self[0].type == 'setup') else None

    @property
    def teardown(self):
        return self[-1] if (self and self[-1].type == 'teardown') else None

    @property
    def all(self):
        return self

    @property
    def normal(self):
        for kw in self:
            if kw.type in ('kw', 'for', 'foritem'):
                yield kw
