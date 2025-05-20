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

from collections.abc import Sequence

from robot.result import Keyword
from robot.utils import MultiMatcher


class ExpandKeywordMatcher:

    def __init__(self, expand_keywords: "str|Sequence[str]"):
        self.matched_ids: "list[str]" = []
        if not expand_keywords:
            expand_keywords = []
        elif isinstance(expand_keywords, str):
            expand_keywords = [expand_keywords]
        names = [n[5:] for n in expand_keywords if n[:5].lower() == "name:"]
        tags = [p[4:] for p in expand_keywords if p[:4].lower() == "tag:"]
        self._match_name = MultiMatcher(names).match
        self._match_tags = MultiMatcher(tags).match_any

    def match(self, kw: Keyword):
        match = self._match_name(kw.full_name or "") or self._match_tags(kw.tags)
        if match and not kw.not_run:
            self.matched_ids.append(kw.id)
