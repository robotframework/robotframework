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

from robot import utils


class Tags(object):

    def __init__(self, tags=None):
        if isinstance(tags, basestring):
            tags = [tags]
        self._tags = utils.normalize_tags(tags or [])

    def add(self, tags):
        self._tags = utils.normalize_tags(list(self) + list(Tags(tags)))

    def remove(self, tags):
        tags = TagPatterns(tags)
        self._tags = [t for t in self if not tags.match(t)]

    def __contains__(self, tag):
        return TagPatterns(tag).match_any(self)

    def __len__(self):
        return len(self._tags)

    def __iter__(self):
        return iter(self._tags)

    def __unicode__(self):
        return u'[%s]' % ', '.join(self)

    def __str__(self):
        return unicode(self).encode('UTF-8')


class TagPatterns(object):

    def __init__(self, patters):
        self._patterns = list(Tags(patters))

    def match(self, tag):
        return any(utils.matches(tag, p, ignore=['_']) for p in self._patterns)

    def match_any(self, tags):
        return any(self.match(t) for t in tags)

    def __contains__(self, tag):
        return self.match(tag)

    def __len__(self):
        return len(self._patterns)

    def __iter__(self):
        return iter(self._patterns)
