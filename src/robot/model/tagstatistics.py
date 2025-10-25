#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

from robot.utils import NormalizedDict

from .stats import CombinedTagStat, TagStat
from .tags import TagPatterns


class TagStatistics:
    """Container for tag statistics."""

    def __init__(self, combined_stats):
        self.tags = NormalizedDict(ignore="_")
        self.combined = combined_stats

    def visit(self, visitor):
        visitor.visit_tag_statistics(self)

    def __iter__(self):
        return iter(sorted([*self.combined, *self.tags.values()]))


class TagStatisticsBuilder:

    def __init__(
        self,
        included=None,
        excluded=None,
        combined=None,
        docs=None,
        links=None,
    ):
        self._included = TagPatterns(included)
        self._excluded = TagPatterns(excluded)
        self._reserved = TagPatterns("robot:*")
        self._info = TagStatInfo(docs, links)
        self.stats = TagStatistics(self._info.get_combined_stats(combined))

    def add_test(self, test):
        self._add_tags_to_statistics(test)
        self._add_to_combined_statistics(test)

    def _add_tags_to_statistics(self, test):
        for tag in test.tags:
            if self._is_included(tag) and not self._suppress_reserved(tag):
                if tag not in self.stats.tags:
                    self.stats.tags[tag] = self._info.get_stat(tag)
                self.stats.tags[tag].add_test(test)

    def _is_included(self, tag):
        if self._included and tag not in self._included:
            return False
        return tag not in self._excluded

    def _suppress_reserved(self, tag):
        return tag in self._reserved and tag not in self._included

    def _add_to_combined_statistics(self, test):
        for stat in self.stats.combined:
            if stat.match(test.tags):
                stat.add_test(test)


class TagStatInfo:

    def __init__(self, docs=None, links=None):
        self._docs = [TagStatDoc(*doc) for doc in docs or []]
        self._links = [TagStatLink(*link) for link in links or []]

    def get_stat(self, tag):
        return TagStat(tag, self.get_doc(tag), self.get_links(tag))

    def get_combined_stats(self, combined=None):
        return [self._get_combined_stat(*comb) for comb in combined or []]

    def _get_combined_stat(self, pattern, name=None):
        name = name or pattern
        return CombinedTagStat(
            pattern,
            name,
            self.get_doc(name),
            self.get_links(name),
        )

    def get_doc(self, tag):
        return " & ".join(doc.text for doc in self._docs if doc.match(tag))

    def get_links(self, tag):
        return [link.get_link(tag) for link in self._links if link.match(tag)]


class TagStatDoc:

    def __init__(self, pattern, doc):
        self._matcher = TagPatterns(pattern)
        self.text = doc

    def match(self, tag):
        return self._matcher.match(tag)


class TagStatLink:
    _match_pattern_tokenizer = re.compile(r"(\*|\?+)")

    def __init__(self, pattern, link, title):
        self._regexp = self._get_match_regexp(pattern)
        self._link = link
        self._title = title.replace("_", " ")

    def match(self, tag):
        return self._regexp.match(tag) is not None

    def get_link(self, tag):
        match = self._regexp.match(tag)
        if not match:
            return None
        link, title = self._replace_groups(self._link, self._title, match)
        return link, title

    def _replace_groups(self, link, title, match):
        for index, group in enumerate(match.groups(), start=1):
            placefolder = f"%{index}"
            link = link.replace(placefolder, group)
            title = title.replace(placefolder, group)
        return link, title

    def _get_match_regexp(self, pattern):
        pattern = "".join(self._yield_match_pattern(pattern))
        return re.compile(pattern, re.IGNORECASE)

    def _yield_match_pattern(self, pattern):
        yield "^"
        for token in self._match_pattern_tokenizer.split(pattern):
            if token.startswith("?"):
                yield f"({'.' * len(token)})"
            elif token == "*":
                yield "(.*)"
            else:
                yield re.escape(token)
        yield "$"
