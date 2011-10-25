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
from robot.common.statistics import CriticalStats, AllStats


class TestSuite(object):

    def __init__(self, parent=None, source='', name='', doc='', metadata=None,
                 status='UNDEFINED'):
        self.parent = parent
        self.source = source
        self.name = name
        self.doc = doc
        self.metadata = metadata
        self.status = status
        self.message = ''
        self.keywords = []
        self.suites = []
        self.tests = []
        self.starttime = ''
        self.endtime = ''
        self.elapsedtime = ''

    @property
    def critical_stats(self):
        return CriticalStats(self)

    @property
    def all_stats(self):
        return AllStats(self)

    @property
    def longname(self):
        if self.parent:
            return self.parent.longname + '.' + self.name
        return self.name

    def _get_metadata(self):
        return self._metadata
    def _set_metadata(self, metadata):
        self._metadata = Metadata(metadata)
    metadata = property(_get_metadata, _set_metadata)

    def _get_suites(self):
        return self._suites
    def _set_suites(self, suites):
        self._suites = TestSuites(self, suites)
    suites = property(_get_suites, _set_suites)

    def _get_tests(self):
        return self._tests
    def _set_tests(self, tests):
        self._tests = TestCases(self, tests)
    tests = property(_get_tests, _set_tests)

    def _get_keywords(self):
        return self._keywords
    def _set_keywords(self, keywords):
        self._keywords = Keywords(self, keywords)
    keywords = property(_get_keywords, _set_keywords)

    def set_tags(self, add=None, remove=None):
        for test in self.tests:
            test.tags.add(add)
            test.tags.remove(remove)
        for sub in self.suites:
            sub.set_tags(add, remove)


class TestCase(object):

    def __init__(self, parent=None, name='', doc='', tags=None,
                 status='UNDEFINED', critical=True):
        self.parent = parent
        self.name = name
        self.doc = doc
        self.tags = tags
        self.status = status
        self.message = ''
        self.timeout = ''
        self.critical = critical
        self.keywords = []
        self.starttime = ''
        self.endtime = ''
        self.elapsedtime = ''

    tags = property(lambda self: self._tags,
                    lambda self, tags: setattr(self, '_tags', Tags(tags)))

    def _get_keywords(self):
        return self._keywords
    def _set_keywords(self, keywords):
        self._keywords = Keywords(self, keywords)
    keywords = property(_get_keywords, _set_keywords)


class Keyword(object):

    def __init__(self, parent=None, name='', doc='', type='kw', status='UNDEFINED'):
        self.parent = parent
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
        self.timeout = ''

    def _get_keywords(self):
        return self._keywords
    def _set_keywords(self, keywords):
        self._keywords = Keywords(self, keywords)
    keywords = property(_get_keywords, _set_keywords)

    def _get_messages(self):
        return self._messages
    def _set_messages(self, messages):
        self._messages = Messages(self, messages)
    messages = property(_get_messages, _set_messages)


class Message(object):

    def __init__(self, message='', level='INFO', html=False, timestamp='',
                 linkable=False):
        self.message = message
        self.level = level
        self.html = html
        self.timestamp = timestamp
        self.linkable = linkable


class _ItemList(object):

    def __init__(self, parent, items=None):
        self._parent = parent
        self._items = []
        for item in items or []:
            self.add(item)

    def create(self, **args):
        self._items.append(self._item_class(self._parent, **args))
        return self._items[-1]

    def add(self, item):
        item.parent = self._parent
        self._items.append(item)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __len__(self):
        return len(self._items)


class TestSuites(_ItemList):
    _item_class = TestSuite

class TestCases(_ItemList):
    _item_class = TestCase

class Keywords(_ItemList):
    _item_class = Keyword

class Messages(_ItemList):
    _item_class = Message


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
        tags = Tags(tags)
        self._tags = [t for t in self if t not in tags]

    def __contains__(self, tag):
        return utils.eq_any(tag, list(self), ignore=['_'])

    def __len__(self):
        return len(self._tags)

    def __iter__(self):
        return iter(self._tags)

    def __unicode__(self):
        return u'[%s]' % ', '.join(self)

    def __str__(self):
        return unicode(self).encode('UTF-8')
