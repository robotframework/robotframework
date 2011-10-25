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

    def _get_metadata(self):
        return self._metadata
    def _set_metadata(self, metadata):
        self._metadata = utils.NormalizedDict(metadata, ignore=['_'])
    metadata = property(_get_metadata, _set_metadata)

    def create_keyword(self, name):
        keyword = Keyword(name=name)
        self.keywords.append(keyword)
        return keyword
    def create_test(self, name):
        test = TestCase(self, name)
        self.tests.append(test)
        return test
    def create_suite(self):
        suite = TestSuite()
        self.suites.append(suite)
        return suite


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

    def create_keyword(self, name):
        keyword = Keyword(name=name)
        self.keywords.append(keyword)
        return keyword


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


class Keyword(object):

    def __init__(self, parent=None, name='', doc='', status='UNDEFINED', type='kw'):
        self.parent = parent
        self.name = name
        self.doc = doc
        self.status = status
        self.type = type
        self.args = []
        self.messages = []
        self.keywords = []
        self.children = []
        self.starttime = ''
        self.endtime = ''
        self.elapsedtime = ''
        self.timeout = ''

    def create_keyword(self, name):
        keyword = Keyword(self, name=name)
        self.keywords.append(keyword)
        self._add_child(keyword)
        return keyword

    def create_message(self):
        msg = Message()
        self.messages.append(msg)
        self._add_child(msg)
        return msg

    def _add_child(self, child):
        self.children.append(child)


class Message(object):

    def __init__(self, message='', level='INFO', html=False, timestamp='',
                 linkable=False):
        self.message = message
        self.level = level
        self.html = html
        self.timestamp = timestamp
        self.linkable = linkable


class _ItemList(object):

    def __init__(self, parent):
        self._parent = parent
        self._items = []

    def create(self, **args):
        self._items.append(self._item_class(self._parent, **args))
        return self._items[-1]

    def add(self, item):
        item.parent = self._parent
        self._items.append(item)

    def __iter__(self):
        return iter(self._items)


class TestSuites(_ItemList):
    _item_class = TestSuite

class TestCases(_ItemList):
    _item_class = TestCase

class Keywords(_ItemList):
    _item_class = Keyword
