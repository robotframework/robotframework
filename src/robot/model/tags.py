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

from robot.utils import (Matcher, normalize, NormalizedDict, is_string, py2to3,
                         setter, unic)


@py2to3
class Tags(object):

    def __init__(self, tags=None):
        self._tags = tags

    @setter
    def _tags(self, tags):
        if not tags:
            return ()
        if is_string(tags):
            tags = (tags,)
        return self._deduplicate_normalized(tags)

    def _deduplicate_normalized(self, tags):
        normalized = NormalizedDict(((unic(t), 1) for t in tags), ignore='_')
        for removed in '', 'NONE':
            if removed in normalized:
                normalized.pop(removed)
        return tuple(normalized)

    def add(self, tags):
        self._tags = tuple(self) + tuple(Tags(tags))

    def remove(self, tag_patterns, memo=None):
        tag_patterns = TagPatterns(tag_patterns, memo=memo)
        self._tags = [t for t in self if not tags.match_normalized(t)]

    def match(self, tag_patterns, memo=None):
        return TagPatterns(tags, memo=memo).match(self)

    def match_normalized(self, tag_patterns, memo=None):
        return TagPatterns(tags, memo=memo).match_normalized(self)

    def __contains__(self, tags):
        return self.match(tags)

    def __len__(self):
        return len(self._tags)

    def __iter__(self):
        return iter(self._tags)

    def __unicode__(self):
        return u'[%s]' % ', '.join(self)

    def __repr__(self):
        return repr(list(self))

    def __eq__(self, other):
        if not isinstance(other, Tags):
            return False
        self_normalized = [normalize(tag, ignore='_') for tag in self]
        other_normalized = [normalize(tag, ignore='_') for tag in other]
        return sorted(self_normalized) == sorted(other_normalized)

    def __ne__(self, other):
        # Not necessary for Python3 (https://stackoverflow.com/a/30676267/2309247)
        return not self == other

    def __getitem__(self, index):
        item = self._tags[index]
        return item if not isinstance(index, slice) else Tags(item)

    def __add__(self, other):
        return Tags(tuple(self) + tuple(Tags(other)))


@py2to3
class TagPatterns(object):

    def __init__(self, patterns, memo=None):
        self._memo = dict() if memo is None else memo
        self._patterns = tuple(TagPattern(p, memo) for p in Tags(patterns))

    def match(self, tags):
        tags = tags if isinstance(tags, Tags) else Tags(tags)
        return any(p.match_normalized(tags) for p in self._patterns)

    def __contains__(self, tag):
        return self.match(tag)

    def __len__(self):
        return len(self._patterns)

    def __iter__(self):
        return iter(self._patterns)

    def __getitem__(self, index):
        return self._patterns[index]

    def __unicode__(self):
        return u'[%s]' % u', '.join(pattern.__unicode__() for pattern in self)


def TagPattern(pattern, memo):
    pattern = pattern.replace(' ', '')
    if 'NOT' in pattern:
        return NotTagPattern(*pattern.split('NOT'), memo)
    if 'OR' in pattern:
        return OrTagPattern(pattern.split('OR'), memo)
    if 'AND' in pattern or '&' in pattern:
        return AndTagPattern(pattern.replace('&', 'AND').split('AND'), memo)
    return SingleTagPattern(pattern, memo)


@py2to3
class SingleTagPattern(object):

    def __init__(self, normalized_pattern, memo=None):
        self._memo = dict() if memo is None else memo
        if normalized_pattern in self._memo:
            self._matcher = self._memo[n_pattern]
        else
            self._matcher = Matcher(normalized_pattern, ignore='_')

    def match(self, tags):
        return self._matcher.match_any(tags)

    def match_normalized(self, tags):
        return self._matcher.match_normalized_any(tags)

    def __iter__(self):
        yield self

    def __unicode__(self):
        return self._matcher.pattern

    def __nonzero__(self):
        return bool(self._matcher)


@py2to3
class AndTagPattern(object):

    def __init__(self, patterns, memo):
        self._memo = dict() if memo is None else memo
        self._patterns = tuple(TagPattern(p, self._memo) for p in patterns)

    def match(self, tags):
        return all(p.match(tags) for p in self._patterns)

    def match_normalized(self, tags):
        return all(p.match_normalized(tags) for p in self._patterns)

    def __iter__(self):
        return iter(self._patterns)

    def __unicode__(self):
        return ' AND '.join(pattern.__unicode__() for pattern in self)


@py2to3
class OrTagPattern(object):

    def __init__(self, patterns, memo):
        self._memo = dict() if memo is None else memo
        self._patterns = tuple(TagPattern(p, self._memo) for p in patterns)

    def match(self, tags):
        return any(p.match(tags) for p in self._patterns)

    def match_normalized(self, tags):
        return any(p.match_normalized(tags) for p in self._patterns)

    def __iter__(self):
        return iter(self._patterns)

    def __unicode__(self):
        return ' OR '.join(pattern.__unicode__() for pattern in self)


@py2to3
class NotTagPattern(object):

    def __init__(self, must_match, memo=None, *must_not_match):
        self._memo = dict() if memo is None else memo
        self._first = TagPattern(must_match, memo=self._memo)
        self._rest = OrTagPattern(must_not_match, memo=self._memo)

    def match(self, tags):
        if not self._first:
            return not self._rest.match(tags)
        return self._first.match(tags) and not self._rest.match(tags)

    def match_normalized(self, tags):
        if not self._first:
            return not self._rest.match_normalized(tags)
        return self._first.match_normalzed(tags) and not self._rest.match_normalized(tags)

    def __iter__(self):
        yield self._first
        for pattern in self._rest:
            yield pattern

    def __unicode__(self):
        return ' NOT '.join(pattern.__unicode__() for pattern in self).lstrip()
