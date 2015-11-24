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

from robot.utils import py2to3

from .tags import TagPatterns


@py2to3
class Criticality(object):

    def __init__(self, critical_tags=None, non_critical_tags=None):
        self.critical_tags = self._get_tag_patterns(critical_tags)
        self.non_critical_tags = self._get_tag_patterns(non_critical_tags)

    def _get_tag_patterns(self, tags):
        return TagPatterns(tags) if not isinstance(tags, TagPatterns) else tags

    def tag_is_critical(self, tag):
        return self.critical_tags.match(tag)

    def tag_is_non_critical(self, tag):
        return self.non_critical_tags.match(tag)

    def test_is_critical(self, test):
        if self.critical_tags and not self.critical_tags.match(test.tags):
            return False
        return not self.non_critical_tags.match(test.tags)

    def __nonzero__(self):
        return bool(self.critical_tags or self.non_critical_tags)
