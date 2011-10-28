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

from itertools import chain
from robot.common.model import _Critical

from robot.common.statistics import CriticalStats, AllStats, Statistics
from robot.output.loggerhelper import Message as BaseMessage
from robot import utils


class ExecutionResult(object):

    def __init__(self):
        self.errors = ExecutionErrors()
        self.suite = TestSuite()

    @property
    def statistics(self):
        return Statistics(self.suite)

    def visit(self, visitor):
        self.suite.visit(visitor)
        self.statistics.visit(visitor)
        self.errors.visit(visitor)


class CombinedExecutionResult(ExecutionResult):

    def __init__(self, *others):
        ExecutionResult.__init__(self)
        for other in others:
            self.add_result(other)

    def add_result(self, other):
        self.suite.suites.append(other.suite)
        self.errors.add(other.errors)


class ExecutionErrors(object):

    def __init__(self):
        self.messages = ItemList(Message)

    def add(self, other):
        self.messages.extend(other.messages)

    def visit(self, visitor):
        visitor.start_errors()
        for message in self.messages:
            message.visit(visitor)
        visitor.end_errors()


class TestSuite(object):

    def __init__(self, source='', name='', doc='', metadata=None):
        self.parent = None
        self.source = source
        self.name = name
        self.doc = doc
        self.metadata = metadata
        self.message = ''
        self.keywords = []
        self.suites = []
        self.tests = []
        self.starttime = 'N/A'
        self.endtime = 'N/A'

    def _get_name(self):
        return self._name or ' & '.join(s.name for s in self.suites)
    def _set_name(self, name):
        self._name = name
    name = property(_get_name, _set_name)

    def _get_status(self):
        return 'PASS' if not self.critical_stats.failed else 'FAIL'
        #TODO: Setter exists but is ignored for builders API compatibility
    status = property(_get_status, lambda self,_: 0)

    #TODO: Remove this asap
    @property
    def critical(self):
        return _Critical()

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
        return ItemList(Keyword, keywords, parent=self)

    @property
    def id(self):
        if not self.parent:
            return 's1'
        return self.parent.id + '-s%d' % (list(self.parent.suites).index(self)+1)

    @property
    def critical_stats(self):
        return CriticalStats(self)

    @property
    def all_stats(self):
        return AllStats(self)

    @property
    def elapsedtime(self):
        if self.starttime == 'N/A' or self.endtime == 'N/A':
            return sum(s.elapsedtime for s in self.suites)
        return utils.get_elapsed_time(self.starttime, self.endtime)

    @property
    def longname(self):
        if self.parent:
            return self.parent.longname + '.' + self.name
        return self.name

    def set_tags(self, add=None, remove=None):
        for test in self.tests:
            test.tags.add(add)
            test.tags.remove(remove)
        for sub in self.suites:
            sub.set_tags(add, remove)

    def visit(self, visitor):
        visitor.start_suite(self)
        for kw in self.keywords:
            kw.visit(visitor)
        for suite in self.suites:
            suite.visit(visitor)
        for test in self.tests:
            test.visit(visitor)
        visitor.end_suite(self)

    def get_metadata(self):
        return self.metadata.items()


class TestCase(object):

    def __init__(self, name='', doc='', tags=None, status='UNDEFINED',
                 critical='yes', starttime='N/A', endtime='N/A'):
        self.parent = None
        self.name = name
        self.doc = doc
        self.tags = tags
        self.status = status
        self.message = ''
        self.timeout = ''
        self.critical = critical
        self.keywords = []
        self.starttime = starttime
        self.endtime = endtime
        self.elapsedtime = ''

    @utils.setter
    def tags(self, tags):
        return Tags(tags)

    @utils.setter
    def keywords(self, keywords):
        return ItemList(Keyword, keywords, parent=self)

    def visit(self, visitor):
        visitor.start_test(self)
        for kw in self.keywords:
            kw.visit(visitor)
        visitor.end_test(self)


class Keyword(object):

    def __init__(self, name='', doc='', type='kw', status='UNDEFINED', timeout=''):
        self.parent = None
        self.name = name
        self.doc = doc
        self.args = []
        self.type = type
        self.status = status
        self.messages = []
        self.keywords = []
        self.starttime = ''
        self.endtime = ''
        self.elapsedtime = ''
        self.timeout = timeout

    @utils.setter
    def keywords(self, keywords):
        return ItemList(Keyword, keywords, parent=self)

    @utils.setter
    def messages(self, messages):
        return ItemList(Message, messages)

    def visit(self, visitor):
        visitor.start_keyword(self)
        for child in chain(self.keywords, self.messages):
            child.visit(visitor)
        visitor.end_keyword(self)


class Message(BaseMessage):

    def __init__(self, message='', level='INFO', html=False, timestamp=None,
                 linkable=False):
        BaseMessage.__init__(self, message, level, html, timestamp, linkable)

    def visit(self, visitor):
        visitor.log_message(self)


class ItemList(object):

    def __init__(self, item_class, items=None, **common_attrs):
        self._item_class = item_class
        self._common_attrs = common_attrs
        self._items = []
        if items:
            self.extend(items)

    def create(self, *args, **kwargs):
        self.append(self._item_class(*args, **kwargs))
        return self._items[-1]

    def append(self, item):
        for name, value in self._common_attrs.items():
            setattr(item, name, value)
        self._items.append(item)

    def extend(self, items):
        for item in items:
            self.append(item)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __len__(self):
        return len(self._items)

    def __unicode__(self):
        return u'[%s]' % ', '.join(self)

    def __str__(self):
        return unicode(self).encode('UTF-8')


class Metadata(utils.NormalizedDict):

    def __init__(self, initial=None):
        utils.NormalizedDict.__init__(self, initial, ignore=['_'])

    def __unicode__(self):
        return u'{%s}' % ', '.join('%s: %s' % (k, self[k]) for k in self)

    def __str__(self):
        return unicode(self).encode('UTF-8')


class Tags(object):

    def __init__(self, tags=None):
        if isinstance(tags, basestring):
            tags = [tags]
        self._tags = utils.normalize_tags(tags or [])

    def add(self, tags):
        self._tags = utils.normalize_tags(list(self) + list(Tags(tags)))

    def remove(self, tags):
        tags = TagPatterns(tags)
        self._tags = [t for t in self if t not in tags]

    def __contains__(self, tag):
        return TagPatterns(tag).contains_any(self)

    def __len__(self):
        return len(self._tags)

    def __iter__(self):
        return iter(self._tags)

    def __unicode__(self):
        return u'[%s]' % ', '.join(self)

    def __str__(self):
        return unicode(self).encode('UTF-8')


class TagPatterns(object):

    def __init__(self, patters):
        self._patterns = list(Tags(patters))

    def __contains__(self, tag):
        return any(utils.matches(tag, p, ignore=['_']) for p in self._patterns)

    def contains_any(self, tags):
        return any(t in self for t in tags)
