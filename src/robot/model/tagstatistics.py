#  Copyright 2008-2015 Nokia Solutions and Networks
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
import re

from robot.utils import NormalizedDict, PY3

from .criticality import Criticality
from .stats import CombinedTagStat, CriticalTagStat, TagStat
from .tags import SingleTagPattern, TagPatterns


if PY3:
    unicode = str


class TagStatistics(object):
    """Container for tag statistics."""

    def __init__(self, critical_stats, non_critical_stats, combined_stats):
        #: Dictionary, where key is the name of the tag as a string and value
        #: is an instance of :class:`~robot.model.stats.TagStat`.
        self.tags = NormalizedDict(ignore='_')
        #: List of :class:`~robot.model.stats.CriticalTagStat` objects.
        self.critical = critical_stats
        #: List of :class:`~robot.model.stats.CriticalTagStat` objects.
        self.non_critical = non_critical_stats
        #: List of :class:`~robot.model.stats.CombinedTagStat` objects.
        self.combined = combined_stats

    def visit(self, visitor):
        visitor.visit_tag_statistics(self)

    def __iter__(self):
        crits = self._get_critical_and_non_critical_matcher()
        tags = [t for t in self.tags.values() if t.name not in crits]
        return iter(sorted(chain(self.critical, self.non_critical,
                                 self.combined, tags)))

    def _get_critical_and_non_critical_matcher(self):
        crits = [stat for stat in self.critical + self.non_critical
                 if isinstance(stat.pattern, SingleTagPattern)]
        return NormalizedDict([(unicode(stat.pattern), None) for stat in crits],
                              ignore='_')


class TagStatisticsBuilder(object):

    def __init__(self, criticality=None, included=None, excluded=None,
                 combined=None, docs=None, links=None):
        self._included = TagPatterns(included)
        self._excluded = TagPatterns(excluded)
        self._info = TagStatInfo(docs, links)
        self.stats = TagStatistics(
            self._info.get_critical_stats(criticality),
            self._info.get_critical_stats(criticality, critical=False),
            self._info.get_combined_stats(combined)
        )

    def add_test(self, test):
        self._add_tags_to_statistics(test)
        self._add_to_critical_and_combined_statistics(test)

    def _add_tags_to_statistics(self, test):
        for tag in test.tags:
            if self._is_included(tag):
                if tag not in self.stats.tags:
                    self.stats.tags[tag] = self._info.get_stat(tag)
                self.stats.tags[tag].add_test(test)

    def _is_included(self, tag):
        if self._included and not self._included.match(tag):
            return False
        return not self._excluded.match(tag)

    def _add_to_critical_and_combined_statistics(self, test):
        stats = self.stats
        for stat in stats.critical + stats.non_critical + stats.combined:
            if stat.match(test.tags):
                stat.add_test(test)


class TagStatInfo(object):

    def __init__(self, docs=None, links=None):
        self._docs = [TagStatDoc(*doc) for doc in docs or []]
        self._links = [TagStatLink(*link) for link in links or []]

    def get_stat(self, tag):
        return TagStat(tag, self.get_doc(tag), self.get_links(tag))

    def get_critical_stats(self, criticality, critical=True):
        if not criticality:
            return []
        tag_patterns = (criticality.critical_tags
                        if critical else criticality.non_critical_tags)
        return [self._get_critical_stat(p, critical) for p in tag_patterns]

    def _get_critical_stat(self, pattern, critical):
        name = unicode(pattern)
        return CriticalTagStat(pattern, name, critical, self.get_doc(name),
                               self.get_links(name))

    def get_combined_stats(self, combined=None):
        return [self._get_combined_stat(*comb) for comb in combined or []]

    def _get_combined_stat(self, pattern, name=None):
        name = name or pattern
        return CombinedTagStat(pattern, name, self.get_doc(name),
                               self.get_links(name))

    def get_doc(self, tag):
        return ' & '.join(doc.text for doc in self._docs if doc.match(tag))

    def get_links(self, tag):
        return [link.get_link(tag) for link in self._links if link.match(tag)]


class TagStatDoc(object):

    def __init__(self, pattern, doc):
        self._matcher = TagPatterns(pattern)
        self.text = doc

    def match(self, tag):
        return self._matcher.match(tag)


class TagStatLink(object):
    _match_pattern_tokenizer = re.compile('(\*|\?+)')

    def __init__(self, pattern, link, title):
        self._regexp = self._get_match_regexp(pattern)
        self._link = link
        self._title = title.replace('_', ' ')

    def match(self, tag):
        return self._regexp.match(tag) is not None

    def get_link(self, tag):
        match = self._regexp.match(tag)
        if not match:
            return None
        link, title = self._replace_groups(self._link, self._title, match)
        return link, title

    def _replace_groups(self, link, title, match):
        for index, group in enumerate(match.groups()):
            placefolder = '%%%d' % (index+1)
            link = link.replace(placefolder, group)
            title = title.replace(placefolder, group)
        return link, title

    def _get_match_regexp(self, pattern):
        pattern = '^%s$' % ''.join(self._yield_match_pattern(pattern))
        return re.compile(pattern, re.IGNORECASE)

    def _yield_match_pattern(self, pattern):
        for token in self._match_pattern_tokenizer.split(pattern):
            if token.startswith('?'):
                yield '(%s)' % ('.'*len(token))
            elif token == '*':
                yield '(.*)'
            else:
                yield re.escape(token)
