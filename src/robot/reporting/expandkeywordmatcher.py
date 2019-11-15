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

from robot.errors import DataError
from robot.model import TagPatterns
from robot.utils import MultiMatcher, is_list_like, py2to3


@py2to3
class ExpandKeywordMatcher(object):

    def __init__(self, expand_keywords):
        self.matched_ids = []
        if not expand_keywords:
            expand_keywords = []
        elif not is_list_like(expand_keywords):
            expand_keywords = [expand_keywords]
        names = [n[5:] for n in expand_keywords if n[:5].lower() == 'name:']
        tags  = [p[4:] for p in expand_keywords if p[:4].lower() == 'tag:']
        self._namematcher = MultiMatcher(names) if names else None
        self._tagmatcher = MultiMatcher(tags) if tags else None

    def check(self, kw):
        if (self._namematcher and self._namematcher.match(kw.kwname)) or \
                (self._tagmatcher and self._tagmatcher.match_any(kw.tags)):
            self.matched_ids.append(kw.id)