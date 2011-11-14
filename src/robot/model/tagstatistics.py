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

from robot.model.tags import TagPatterns
from robot.model.stats import TagStat
from robot import utils


class TagStatistics(object):

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

    def visit(self, visitor):
        visitor.visit_tag_statistics(self)

    def __iter__(self):
        return iter(sorted(self.stats.values()))

    def sort(self):
        # TODO: Is this needed?
        for stat in self.stats.values():
            stat.tests.sort()


class CombinedTag(object):

    def __init__(self, pattern, name):
        self.pattern = pattern
        self._matcher = TagPatterns(pattern)
        self.name = name or pattern

    def match(self, tags):
        return self._matcher.match(tags)


class TagStatInfo(object):

    def __init__(self, docs, links):
        self._docs = [TagStatDoc(*doc) for doc in docs]
        self._links = [TagStatLink(*link) for link in links]

    def get_doc(self, tag):
        return ' & '.join(doc.text for doc in self._docs if doc.matches(tag))

    def get_links(self, tag):
        return [link.get_link(tag) for link in self._links if link.matches(tag)]


class TagStatDoc(object):

    def __init__(self, pattern, doc):
        self.text = doc
        self._pattern = TagPatterns(pattern)

    def matches(self, tag):
        return self._pattern.match(tag)


class TagStatLink(object):
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
