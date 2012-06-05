#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

from robot.utils import normalize_tags, setter, Matcher


class Tags(object):

    def __init__(self, tags=None):
        self._tags = tags

    @setter
    def _tags(self, tags):
        if isinstance(tags, basestring):
            tags = [tags]
        return normalize_tags(tags or [])

    def add(self, tags):
        self._tags = list(self) + list(Tags(tags))

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

    def __unicode__(self):
        return u'[%s]' % ', '.join(self)

    def __str__(self):
        return unicode(self).encode('UTF-8')


class TagPatterns(object):

    def __init__(self, patterns):
        self._patterns = [TagPattern(p) for p in Tags(patterns)]

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


def TagPattern(pattern):
    pattern = pattern.replace('&', 'AND')
    if 'NOT' in pattern:
        return _NotTagPattern(*pattern.split('NOT'))
    if 'AND' in pattern:
        return _AndTagPattern(pattern.split('AND'))
    return _SingleTagPattern(pattern)


class _SingleTagPattern(object):

    def __init__(self, pattern):
        self._matcher = Matcher(pattern, ignore=['_'])

    def match(self, tags):
        return any(self._matcher.match(tag) for tag in tags)

    def __unicode__(self):
        return self._matcher.pattern


class _AndTagPattern(object):

    def __init__(self, patterns):
        self._patterns = [TagPattern(p) for p in patterns]

    def match(self, tags):
        return all(p.match(tags) for p in self._patterns)


class _NotTagPattern(object):

    def __init__(self, must_match, *must_not_match):
        self._must = TagPattern(must_match)
        self._must_not = [TagPattern(m) for m in must_not_match]

    def match(self, tags):
        return self._must.match(tags) \
            and not any(p.match(tags) for p in self._must_not)
