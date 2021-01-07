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

from robot.utils import (Matcher, normalize, NormalizedDict, is_string, py3to2,
                         setter, unic, unicode)


@py3to2
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

    def remove(self, tags):
        tags = TagPatterns(tags)
        self._tags = [t for t in self if not tags.match(t)]

    def match(self, tags):
        return TagPatterns(tags).match(self)

    def __contains__(self, tags):
        return self.match(tags)

    def __len__(self):
        return len(self._tags)

    def __iter__(self):
        return iter(self._tags)

    def __str__(self):
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
        return not self == other

    def __getitem__(self, index):
        item = self._tags[index]
        return item if not isinstance(index, slice) else Tags(item)

    def __add__(self, other):
        return Tags(tuple(self) + tuple(Tags(other)))


@py3to2
class TagPatterns(object):

    def __init__(self, patterns):
        self._patterns = tuple(TagPattern(p) for p in Tags(patterns))

    def match(self, tags):
        tags = tags if isinstance(tags, Tags) else Tags(tags)
        return any(p.match(tags) for p in self._patterns)

    def __contains__(self, tag):
        return self.match(tag)

    def __len__(self):
        return len(self._patterns)

    def __iter__(self):
        return iter(self._patterns)

    def __getitem__(self, index):
        return self._patterns[index]

    def __str__(self):
        return u'[%s]' % u', '.join(unicode(pattern) for pattern in self)


def TagPattern(pattern):
    pattern = pattern.replace(' ', '')
    if 'NOT' in pattern:
        return NotTagPattern(*pattern.split('NOT'))
    if 'OR' in pattern:
        return OrTagPattern(pattern.split('OR'))
    if 'AND' in pattern or '&' in pattern:
        return AndTagPattern(pattern.replace('&', 'AND').split('AND'))
    return SingleTagPattern(pattern)


@py3to2
class SingleTagPattern(object):

    def __init__(self, pattern):
        self._matcher = Matcher(pattern, ignore='_')

    def match(self, tags):
        return self._matcher.match_any(tags)

    def __iter__(self):
        yield self

    def __str__(self):
        return self._matcher.pattern

    def __bool__(self):
        return bool(self._matcher)


@py3to2
class AndTagPattern(object):

    def __init__(self, patterns):
        self._patterns = tuple(TagPattern(p) for p in patterns)

    def match(self, tags):
        return all(p.match(tags) for p in self._patterns)

    def __iter__(self):
        return iter(self._patterns)

    def __str__(self):
        return ' AND '.join(unicode(pattern) for pattern in self)


@py3to2
class OrTagPattern(object):

    def __init__(self, patterns):
        self._patterns = tuple(TagPattern(p) for p in patterns)

    def match(self, tags):
        return any(p.match(tags) for p in self._patterns)

    def __iter__(self):
        return iter(self._patterns)

    def __str__(self):
        return ' OR '.join(unicode(pattern) for pattern in self)


@py3to2
class NotTagPattern(object):

    def __init__(self, must_match, *must_not_match):
        self._first = TagPattern(must_match)
        self._rest = OrTagPattern(must_not_match)

    def match(self, tags):
        if not self._first:
            return not self._rest.match(tags)
        return self._first.match(tags) and not self._rest.match(tags)

    def __iter__(self):
        yield self._first
        for pattern in self._rest:
            yield pattern

    def __str__(self):
        return ' NOT '.join(unicode(pattern) for pattern in self).lstrip()
