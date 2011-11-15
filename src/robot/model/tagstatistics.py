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
from .tags import TagPatterns
from .stats import TagStat, CombinedTagStat


class TagStatistics(object):

    def __init__(self, criticality, include=None, exclude=None, combine=None,
                 docs=None, links=None):
        # TODO: Check argument names
        self.tags = utils.NormalizedDict(ignore=['_'])
        self._include = TagPatterns(include)
        self._exclude = TagPatterns(exclude)
        self._info = TagStatInfo(criticality, docs, links)
        self.combined = [self._info.get_combined_stat(pattern, name)
                         for pattern, name in combine or []]

    def add_test(self, test):
        self._add_tags_to_statistics(test)
        self._add_to_combined_statistics(test)

    def _add_tags_to_statistics(self, test):
        for tag in test.tags:
            if self._is_included(tag):
                if tag not in self.tags:
                    self.tags[tag] = self._info.get_stat(tag)
                self.tags[tag].add_test(test)

    def _is_included(self, tag):
        if self._include and not self._include.match(tag):
            return False
        return not self._exclude.match(tag)

    def _add_to_combined_statistics(self, test):
        for comb in self.combined:
            if comb.match(test.tags):
                comb.add_test(test)

    def visit(self, visitor):
        visitor.visit_tag_statistics(self)

    def __iter__(self):
        return iter(sorted(self.tags.values() + self.combined))

    def __len__(self):
        return len(self.tags) + len(self.combined)


class TagStatInfo(object):

    def __init__(self, criticality, docs=None, links=None):
        self._criticality = criticality
        self._docs = [TagStatDoc(*doc) for doc in docs or []]
        self._links = [TagStatLink(*link) for link in links or []]

    def get_stat(self, tag):
        return TagStat(tag, self._get_doc(tag), self._get_links(tag),
                       self._criticality.is_critical(tag),
                       self._criticality.is_non_critical(tag))

    def get_combined_stat(self, pattern, name=None):
        name = name or pattern
        return CombinedTagStat(pattern, name, self._get_doc(name),
                               self._get_links(name))

    def _get_doc(self, tag):
        return ' & '.join(doc.text for doc in self._docs if doc.match(tag))

    def _get_links(self, tag):
        return [link.get_link(tag) for link in self._links if link.match(tag)]


class TagStatDoc(object):

    def __init__(self, pattern, doc):
        self._matcher = TagPatterns(pattern)
        self.text = doc

    def match(self, tag):
        return self._matcher.match(tag)


class TagStatLink(object):
    _match_pattern_tokenizer = re.compile('(\*|\?)')

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
