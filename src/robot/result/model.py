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

from robot.common.statistics import CriticalStats, AllStats, Statistics
from robot.output.loggerhelper import Message as BaseMessage
from robot import utils
from robot.model import Tags, Critical

from tagsetter import TagSetter
from filter import Filter, MessageFilter
from configurer import SuiteConfigurer
from keywordremover import KeywordRemover


class ExecutionResult(object):

    def __init__(self):
        self.suite = TestSuite()
        self.errors = ExecutionErrors()
        self.generator = None
        self.should_return_status_rc = True
        self._stat_opts = ()

    @property
    def statistics(self):
        return Statistics(self.suite, *self._stat_opts)

    @property
    def return_code(self):
        if self.should_return_status_rc:
            return min(self.suite.critical_stats.failed, 250)
        return 0

    def configure(self, status_rc=True, **suite_opts):
        self.should_return_status_rc = status_rc
        SuiteConfigurer(**suite_opts).configure(self.suite)

    def configure_statistics(self, *stat_opts): #TODO: use **kwargs
        self._stat_opts = stat_opts

    def visit(self, visitor):
        visitor.visit_result(self)


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
        self._critical = None

    def _get_name(self):
        return self._name or ' & '.join(s.name for s in self.suites)
    def _set_name(self, name):
        self._name = name
    name = property(_get_name, _set_name)

    @property
    def status(self):
        return 'PASS' if not self.critical_stats.failed else 'FAIL'

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
    def stat_message(self):
        return self._stat_message()

    @property
    def full_message(self):
        stat_msg = self._stat_message()
        if not self.message:
            return stat_msg
        return '%s\n\n%s' % (self.message, stat_msg)

    def _stat_message(self):
        # TODO: Should create self.statistics and move this there.
        ctotal, cend, cpass, cfail = self._get_counts(self.critical_stats)
        atotal, aend, apass, afail = self._get_counts(self.all_stats)
        return ('%d critical test%s, %d passed, %d failed\n'
                '%d test%s total, %d passed, %d failed'
                % (ctotal, cend, cpass, cfail, atotal, aend, apass, afail))

    def _get_counts(self, stat):
        ending = utils.plural_or_not(stat.total)
        return stat.total, ending, stat.passed, stat.failed

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
            children = list(self.suites) + list(self.tests) + list(self.keywords)
            return sum(item.elapsedtime for item in children)
        return utils.get_elapsed_time(self.starttime, self.endtime)

    @property
    def longname(self):
        if self.parent:
            return self.parent.longname + '.' + self.name
        return self.name

    @property
    def test_count(self):
        return self.all_stats.total

    def set_tags(self, add=None, remove=None):
        self.visit(TagSetter(add, remove))

    def remove_keywords(self, how):
        self.visit(KeywordRemover(how))

    def filter(self, included_suites=None, included_tests=None,
               included_tags=None, excluded_tags=None):
        self.visit(Filter(included_suites, included_tests,
                          included_tags, excluded_tags))

    def filter_messages(self, log_level):
        self.visit(MessageFilter(log_level))

    def visit(self, visitor):
        visitor.visit_suite(self)

    # TODO: Remove and change clients to use metadata.items() directly
    def get_metadata(self):
        return self.metadata.items()

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('UTF-8')

    def __repr__(self):
        return repr(str(self))


class TestCase(object):

    def __init__(self, name='', doc='', tags=None, status='UNDEFINED',
                timeout='', starttime='N/A', endtime='N/A'):
        self.parent = None
        self.name = name
        self.doc = doc
        self.tags = tags
        self.status = status
        self.message = ''
        self.timeout = timeout
        self.keywords = []
        self.starttime = starttime
        self.endtime = endtime
        self._critical = 'yes'

    @utils.setter
    def tags(self, tags):
        return Tags(tags)

    @utils.setter
    def keywords(self, keywords):
        return Keywords(keywords, parent=self)

    @property
    def elapsedtime(self):
        return utils.get_elapsed_time(self.starttime, self.endtime)

    @property
    def longname(self):
        if self.parent:
            return self.parent.longname + '.' + self.name
        return self.name

    @property
    def critical(self):
        return 'yes' if self.parent.critical.test_is_critical(self) else 'no'

    @property
    def is_passed(self):
        return self.status == 'PASS'

    # TODO: Remove, move to where statistics are created.
    def is_included(self, includes, excludes):
        return self.tags.match(includes) and not self.tags.match(excludes)

    def visit(self, visitor):
        visitor.visit_test(self)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('UTF-8')

    def __repr__(self):
        return repr(str(self))


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
        self.timeout = timeout

    @utils.setter
    def keywords(self, keywords):
        return Keywords(keywords, parent=self)

    @utils.setter
    def messages(self, messages):
        return ItemList(Message, messages)

    @property
    def elapsedtime(self):
        return utils.get_elapsed_time(self.starttime, self.endtime)

    @property
    def is_passed(self):
        return self.status == 'PASS'

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


class Message(BaseMessage):

    def __init__(self, message='', level='INFO', html=False, timestamp=None,
                 linkable=False):
        BaseMessage.__init__(self, message, level, html, timestamp, linkable)

    def visit(self, visitor):
        visitor.visit_message(self)


class ItemList(object):

    def __init__(self, item_class, items=None, parent=None):
        self._item_class = item_class
        self._parent = parent
        self._items = ()
        if items:
            self.extend(items)

    def create(self, *args, **kwargs):
        self.append(self._item_class(*args, **kwargs))
        return self._items[-1]

    def append(self, item):
        if not isinstance(item, self._item_class):
            raise TypeError("Only '%s' objects accepted, got '%s'"
                            % (self._item_class.__name__, type(item).__name__))
        if self._parent:
            item.parent = self._parent
        self._items = tuple(list(self._items)+[item])

    def extend(self, items):
        for item in items:
            self.append(item)

    def visit(self, visitor):
        for item in self:
            item.visit(visitor)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __len__(self):
        return len(self._items)

    def __unicode__(self):
        return u'[%s]' % ', '.join(unicode(item) for item in self)

    def __str__(self):
        return unicode(self).encode('UTF-8')


class Keywords(ItemList):

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


class Metadata(utils.NormalizedDict):

    def __init__(self, initial=None):
        utils.NormalizedDict.__init__(self, initial, ignore=['_'])

    def __unicode__(self):
        return u'{%s}' % ', '.join('%s: %s' % (k, self[k]) for k in self)

    def __str__(self):
        return unicode(self).encode('UTF-8')
