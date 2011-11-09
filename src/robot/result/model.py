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
from robot import model, utils

from messagefilter import MessageFilter
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

    # TODO: 1) Use **kwargs. 2) Combine with configure?
    def configure_statistics(self, *stat_opts):
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
        # TODO: Handle somehow correctly. Probably Messages class is best approach.
        from robot.model.itemlist import ItemList
        from robot.model import Message
        self.messages = ItemList(Message)

    def add(self, other):
        self.messages.extend(other.messages)

    def visit(self, visitor):
        visitor.start_errors()
        for message in self.messages:
            message.visit(visitor)
        visitor.end_errors()


class TestSuite(model.TestSuite):
    __slots__ = ['message', 'starttime', 'endtime']

    def __init__(self, source='', name='', doc='', metadata=None):
        model.TestSuite.__init__(self, source, name, doc, metadata)
        self.message = ''
        self.starttime = 'N/A'
        self.endtime = 'N/A'

    @property
    def status(self):
        return 'PASS' if not self.critical_stats.failed else 'FAIL'

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

    def remove_keywords(self, how):
        self.visit(KeywordRemover(how))

    def filter_messages(self, log_level):
        self.visit(MessageFilter(log_level))


class TestCase(model.TestCase):
    __slots__ = ['status', 'message', 'starttime', 'endtime']

    def __init__(self, name='', doc='', tags=None, timeout='', status='FAIL',
                 message='', starttime='N/A', endtime='N/A'):
        model.TestCase.__init__(self, name, doc, tags, timeout)
        self.status = status
        self.message = message
        self.starttime = starttime
        self.endtime = endtime

    @property
    def elapsedtime(self):
        return utils.get_elapsed_time(self.starttime, self.endtime)

    # TODO: Rename to passed
    @property
    def is_passed(self):
        return self.status == 'PASS'

    # TODO: Remove, move to where statistics are created.
    def is_included(self, includes, excludes):
        return self.tags.match(includes) and not self.tags.match(excludes)


class Keyword(model.Keyword):
    __slots__ = ['status', 'starttime', 'endtime']

    def __init__(self, name='', doc='', args=None, type='kw', timeout='',
                 status='FAIL', starttime='N/A', endtime='N/A'):
        model.Keyword.__init__(self, name, doc, args, type, timeout)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime

    @property
    def elapsedtime(self):
        return utils.get_elapsed_time(self.starttime, self.endtime)

    @property
    def is_passed(self):
        return self.status == 'PASS'


# TODO: Split this module so that classes can set attributes themselves
TestSuite.keyword_class = Keyword
TestSuite.test_class = TestCase
TestCase.keyword_class = Keyword
