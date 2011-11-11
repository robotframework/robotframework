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

import re

from robot import utils
from robot.result.visitor import SuiteVisitor
from robot.model.tags import TagPatterns


class StatisticsBuilder(SuiteVisitor):

    def __init__(self, stats):
        self._stats = stats
        self._parents = []
        self._first = True
        self._current_suite_stat = self._stats.suite

    def start_suite(self, suite):
        if not self._first:
            new  = SuiteStatistics(suite)
            self._current_suite_stat.suites.append(new)
            self._parents.append(self._current_suite_stat)
            self._current_suite_stat = new
        self._current_suite = suite
        self._first = False

    def end_suite(self, suite):
        if self._parents:
            self._parents[-1].all.add_stat(self._current_suite_stat.all)
            self._parents[-1].critical.add_stat(self._current_suite_stat.critical)
            self._current_suite_stat = self._parents.pop(-1)

    def start_test(self, test):
        self._current_suite_stat.add_test(test)
        self._stats.tags.add_test(test, self._current_suite.critical)


class Statistics(object):

    def __init__(self, suite, suite_stat_level=-1, tag_stat_include=None,
                 tag_stat_exclude=None, tag_stat_combine=None, tag_doc=None,
                 tag_stat_link=None):
        self.tags = TagStatistics(tag_stat_include, tag_stat_exclude,
                                  tag_stat_combine, tag_doc, tag_stat_link)
        self.suite = SuiteStatistics(suite, suite_stat_level)
        StatisticsBuilder(self).visit_suite(suite)
        self.tags.sort()
        self.total = TotalStatistics(self.suite)

    #TODO: Replace with visit
    def serialize(self, serializer):
        serializer.start_statistics(self)
        self.total.serialize(serializer)
        self.tags.serialize(serializer)
        self.suite.serialize(serializer)
        serializer.end_statistics(self)

    def visit(self, visitor):
        self.serialize(visitor)


class SuiteStatistics:

    def __init__(self, suite, suite_stat_level=-1):
        self.all = SuiteStat(suite)
        self.critical = SuiteStat(suite)
        self.suites = []
        self._suite_stat_level = suite_stat_level

    def add_test(self, test):
        self.all.add_test(test)
        if test.critical == 'yes':
            self.critical.add_test(test)

    def serialize(self, serializer):
        serializer.start_suite_stats(self)
        self._serialize(serializer, self._suite_stat_level)
        serializer.end_suite_stats(self)

    def _serialize(self, serializer, max_suite_level, suite_level=1):
        self.all.serialize(serializer)
        if max_suite_level < 0 or max_suite_level > suite_level:
            for suite in self.suites:
                suite._serialize(serializer, max_suite_level, suite_level+1)


class Stat(object):

    def __init__(self, name=''):
        self.name = name
        self.passed = 0
        self.failed = 0

    @property
    def total(self):
        return self.passed + self.failed

    def add_stat(self, other):
        self.passed += other.passed
        self.failed += other.failed

    def add_test(self, test):
        if test.status == 'PASS':
            self.passed += 1
        else:
            self.failed += 1

    def fail_all(self):
        self.failed += self.passed
        self.passed = 0

    def add_suite(self, suite):
        for test in suite.tests:
            if self._is_included(test):
                self.add_test(test)
        for suite in suite.suites:
            self.add_stat(self._subsuite_stats(suite))

    def _is_included(self, test):
        return True

    def _subsuite_stats(self, suite):
        return suite.all_stats

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __nonzero__(self):
        return self.failed == 0


class SuiteStat(Stat):
    type = 'suite'

    def __init__(self, suite):
        Stat.__init__(self, suite.name)
        self.longname = suite.longname
        self.id = suite.id

    def serialize(self, serializer):
        serializer.suite_stat(self)


class TagStat(Stat):
    type = 'tag'

    def __init__(self, name, doc='', links=[], critical=False,
                 non_critical=False, combined=''):
        Stat.__init__(self, name)
        self.doc = doc
        self.links = links
        self.critical = critical
        self.non_critical = non_critical
        self.combined = combined
        self.tests = []

    def add_test(self, test):
        Stat.add_test(self, test)
        self.tests.append(test)

    def __cmp__(self, other):
        if self.critical != other.critical:
            return cmp(other.critical, self.critical)
        if self.non_critical != other.non_critical:
            return cmp(other.non_critical, self.non_critical)
        if bool(self.combined) != bool(other.combined):
            return cmp(bool(other.combined), bool(self.combined))
        return cmp(self.name, other.name)

    def serialize(self, serializer):
        serializer.tag_stat(self)


class TotalStat(Stat):
    type = 'total'

    def __init__(self, name, suite_stat):
        Stat.__init__(self, name)
        self.passed = suite_stat.passed
        self.failed = suite_stat.failed

    def serialize(self, serializer):
        serializer.total_stat(self)


class CombinedTag(object):

    def __init__(self, pattern, name):
        self.pattern = pattern
        self._matcher = TagPatterns(pattern)
        self.name = name or pattern

    def match(self, tags):
        return self._matcher.match(tags)


class TagStatistics:

    def __init__(self, include=None, exclude=None, combine=None, docs=None,
                 links=None):
        self.stats = utils.NormalizedDict(ignore=['_'])
        self._include = TagPatterns(include)
        self._exclude = TagPatterns(exclude)
        self._info = TagStatInfo(docs or [], links or [])
        self._combine = self._create_combined(combine or [])

    def _create_combined(self, combines):
        combines = [CombinedTag(pattern, name) for pattern, name in combines]
        for comb in combines:
            self.stats[comb.name] = TagStat(comb.name,
                                            self._info.get_doc(comb.name),
                                            self._info.get_links(comb.name),
                                            combined=comb.pattern)
        return combines

    def add_test(self, test, critical):
        self._add_tags_statistics(test, critical)
        self._add_combined_statistics(test)

    def _add_tags_statistics(self, test, critical):
        for tag in test.tags:
            if not self._is_included(tag):
                continue
            if tag not in self.stats:
                self.stats[tag] = TagStat(tag,
                                          self._info.get_doc(tag),
                                          self._info.get_links(tag),
                                          critical.is_critical(tag),
                                          critical.is_non_critical(tag))
            self.stats[tag].add_test(test)

    def _is_included(self, tag):
        if self._include and not self._include.match(tag):
            return False
        return not self._exclude.match(tag)

    def _add_combined_statistics(self, test):
        for comb in self._combine:
            if comb.match(test.tags):
                self.stats[comb.name].add_test(test)

    def serialize(self, serializer):
        serializer.start_tag_stats(self)
        for stat in sorted(self.stats.values()):
            stat.serialize(serializer)
        serializer.end_tag_stats(self)

    def sort(self):
        # TODO: Is this needed?
        for stat in self.stats.values():
            stat.tests.sort()


class TotalStatistics:

    def __init__(self, suite):
        self.critical = TotalStat('Critical Tests', suite.critical)
        self.all = TotalStat('All Tests', suite.all)

    def serialize(self, serializer):
        serializer.start_total_stats(self)
        self.critical.serialize(serializer)
        self.all.serialize(serializer)
        serializer.end_total_stats(self)


class TagStatInfo:

    def __init__(self, docs, links):
        self._docs = [TagStatDoc(*doc) for doc in docs]
        self._links = [TagStatLink(*link) for link in links]

    def get_doc(self, tag):
        return ' & '.join(doc.text for doc in self._docs if doc.matches(tag))

    def get_links(self, tag):
        return [link.get_link(tag) for link in self._links if link.matches(tag)]


class TagStatDoc:

    def __init__(self, pattern, doc):
        self.text = doc
        self._pattern = TagPatterns(pattern)

    def matches(self, tag):
        return self._pattern.match(tag)


class TagStatLink:
    _match_pattern_tokenizer = re.compile('(\*|\?)')

    def __init__(self, pattern, link, title):
        self._regexp = self._get_match_regexp(pattern)
        self._link = link
        self._title = title.replace('_', ' ')

    def matches(self, tag):
        return self._regexp.match(tag) is not None

    def get_link(self, tag):
        match = self._regexp.match(tag)
        if not match:
            return None
        link, title = self._replace_groups(self._link, self._title, match)
        return link, title

    def _replace_groups(self, link, title, match):
        for index, group in enumerate(match.groups()):
            placefolder = '%' + str(index+1)
            link = link.replace(placefolder, group)
            title = title.replace(placefolder, group)
        return link, title

    def _get_match_regexp(self, pattern):
        regexp = []
        open_parenthesis = False
        for token in self._match_pattern_tokenizer.split(pattern):
            if token == '':
                continue
            if token == '?':
                if not open_parenthesis:
                    regexp.append('(')
                    open_parenthesis = True
                regexp.append('.')
                continue
            if open_parenthesis:
                regexp.append(')')
                open_parenthesis = False
            if token == '*':
                regexp.append('(.*)')
                continue
            regexp.append(re.escape(token))
        if open_parenthesis:
            regexp.append(')')
        return re.compile('^%s$' % ''.join(regexp), re.IGNORECASE)
