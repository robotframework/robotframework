#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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


class Statistics:

    def __init__(self, suite, suite_stat_level=-1, tag_stat_include=None,
                 tag_stat_exclude=None, tag_stat_combine=None, tag_doc=None,
                 tag_stat_link=None):
        self.tags = TagStatistics(tag_stat_include, tag_stat_exclude,
                                  tag_stat_combine, tag_doc, tag_stat_link)
        self.suite = SuiteStatistics(suite, self.tags, suite_stat_level)
        self.total = TotalStatistics(self.suite)
        self.tags.sort()

    def serialize(self, serializer):
        serializer.start_statistics(self)
        self.total.serialize(serializer)
        self.tags.serialize(serializer)
        self.suite.serialize(serializer)
        serializer.end_statistics(self)


class Stat:

    def __init__(self, name=None, doc=None, link=None):
        self.name = name
        self._doc = doc
        self._link = link
        self.passed = 0
        self.failed = 0

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

    def get_doc(self, split_level=-1):
        return self._doc

    def get_link(self, split_level=-1):
        return self._link

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __nonzero__(self):
        return self.failed == 0


class SuiteStat(Stat):
    type = 'suite'

    def __init__(self, suite):
        Stat.__init__(self, suite.name)
        self.get_long_name = suite.get_long_name

    def get_doc(self, split_level=-1):
        return self.get_long_name(split_level)

    def get_link(self, split_level=-1):
        return self.get_long_name(split_level)

    def serialize(self, serializer):
        serializer.suite_stat(self)


class TagStat(Stat):
    type = 'tag'

    def __init__(self, name, critical=False, non_critical=False, info=None):
        doc = info and info.get_doc(name) or None
        Stat.__init__(self, name, doc, link=name)
        self.critical = critical
        self.non_critical = non_critical
        self.combined = False
        self.tests = []
        self.links = info and info.get_links(name) or []

    def add_test(self, test):
        Stat.add_test(self, test)
        self.tests.append(test)

    def __cmp__(self, other):
        if self.critical != other.critical:
            return self.critical is True and -1 or 1
        if self.non_critical != other.non_critical:
            return self.non_critical is True and -1 or 1
        if self.combined != other.combined:
            return self.combined is True and -1 or 1
        return cmp(self.name, other.name)

    def serialize(self, serializer):
        serializer.tag_stat(self)


class CombinedTagStat(TagStat):

    def __init__(self, name):
        TagStat.__init__(self, name)
        self.combined = True


class TotalStat(Stat):
    type = 'total'

    def __init__(self, name, suite_stat):
        Stat.__init__(self, name)
        self.passed = suite_stat.passed
        self.failed = suite_stat.failed

    def serialize(self, serializer):
        serializer.total_stat(self)


class SuiteStatistics:

    def __init__(self, suite, tag_stats, suite_stat_level=-1):
        self.all = SuiteStat(suite)
        self.critical = SuiteStat(suite)
        self.suites = []
        self._process_suites(suite, tag_stats)
        self._process_tests(suite, tag_stats)
        self._suite_stat_level = suite_stat_level

    def _process_suites(self, suite, tag_stats):
        for subsuite in suite.suites:
            substat = SuiteStatistics(subsuite, tag_stats)
            self.suites.append(substat)
            self.all.add_stat(substat.all)
            self.critical.add_stat(substat.critical)

    def _process_tests(self, suite, tag_stats):
        for test in suite.tests:
            self.all.add_test(test)
            if test.critical == 'yes':
                self.critical.add_test(test)
            tag_stats.add_test(test, suite.critical)

    def serialize(self, serializer):
        if self._suite_stat_level == 0:
            return
        serializer.start_suite_stats(self)
        self._serialize(serializer, self._suite_stat_level)
        serializer.end_suite_stats(self)

    def _serialize(self, serializer, max_suite_level, suite_level=1):
        self.all.serialize(serializer)
        if max_suite_level < 0 or max_suite_level > suite_level:
            for suite in self.suites:
                suite._serialize(serializer, max_suite_level, suite_level+1)


class TagStatistics:

    def __init__(self, include=None, exclude=None, tag_stat_combine=None,
                 docs=None, links=None):
        self.stats = utils.NormalizedDict()
        self._include = include or []
        self._exclude = exclude or []
        self._patterns_and_names = self._get_patterns_and_names(tag_stat_combine)
        self._taginfo = TagStatInfo(docs or [], links or [])

    def _get_patterns_and_names(self, tag_stat_combine_options):
        if not tag_stat_combine_options:
            return []
        return [ self._parse_name_and_pattern_from(option) \
                 for option in tag_stat_combine_options ]

    def _parse_name_and_pattern_from(self, option):
        pattern, name = self._split_pattern_and_name(option)
        name = self._get_name(pattern, name)
        return pattern, name

    def _split_pattern_and_name(self, pattern):
        option_separator = ':'
        if not option_separator in pattern:
            return pattern, pattern
        index = pattern.rfind(option_separator)
        return pattern[:index], pattern[index+1:]

    def _get_name(self, pattern, name):
        if pattern != name:
            return name.replace('_', ' ')
        return name.replace('&', ' & ').replace('NOT', ' NOT ')

    def add_test(self, test, critical):
        self._add_tags_statistics(test, critical)
        self._add_tagstatcombine_statistics(test)

    def _add_tags_statistics(self, test, critical):
        for tag in test.tags:
            if not self._is_included(tag):
                continue
            if not self.stats.has_key(tag):
                self.stats[tag] = TagStat(tag, critical.is_critical(tag),
                                          critical.is_non_critical(tag),
                                          self._taginfo)
            self.stats[tag].add_test(test)

    def _is_included(self, tag):
        if self._include != [] and not utils.matches_any(tag, self._include):
            return False
        return not utils.matches_any(tag, self._exclude)

    def _add_tagstatcombine_statistics(self, test):
        for pattern, name in self._patterns_and_names:
            if not self.stats.has_key(name):
                self.stats[name] = CombinedTagStat(name)
            if test.is_included([pattern], []):
                self.stats[name].add_test(test)

    def serialize(self, serializer):
        if not self.stats and (self._include or self._exclude):
            return
        serializer.start_tag_stats(self)
        stats = self.stats.values()
        stats.sort()
        for stat in stats:
            stat.serialize(serializer)
        serializer.end_tag_stats(self)

    def sort(self):
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
        self._docs = [ self._parse_doc(doc) for doc in docs ]
        self._links = [ TagStatLink(*link) for link in links ]

    def _parse_doc(self, cli_item):
        try:
            tag, doc = cli_item.split(':', 1)
        except ValueError:
            tag, doc = cli_item, ''
        return tag, doc

    def get_doc(self, tag):
        docs = []
        for pattern, doc in self._docs:
            if utils.matches(tag, pattern):
                docs.append(doc)
        return docs and ' '.join(docs) or None

    def get_links(self, tag):
        links = [ link.get_link(tag) for link in self._links ]
        return [ link for link in links if link is not None ]


class TagStatLink:
    _match_pattern_tokenizer = re.compile('(\*|\?)')

    def __init__(self, pattern, link, title):
        self._regexp = self._get_match_regexp(pattern)
        self._link = link
        self._title = title.replace('_', ' ')

    def get_link(self, tag):
        match = self._regexp.match(tag)
        if match is not None:
            link = self._replace_matches(self._link, match)
            return link, self._title
        return None

    def _replace_matches(self, url, match):
        groups = match.groups()
        for i, group in enumerate(groups):
            url = url.replace('%%%d' % (i+1), group)
        return url

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
