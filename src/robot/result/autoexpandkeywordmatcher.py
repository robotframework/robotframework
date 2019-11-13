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


def validate_autoexpandkeywords(options):
    for opt in options:
        if not (opt.lower().startswith(('name:', 'tag:')):
            raise DataError("Expected 'TAG:<pattern>', or "
                            "'NAME:<pattern>' but got '%s'." % opt)


@py2to3
class AutoExpandKeywordMatcher(object):

    def __init__(self, auto_expand_list):
        self._matched_ids = []
        if auto_expand_list==None: 
            auto_expand_list=[]
        elif not is_list_like(auto_expand_list):
            auto_expand_list = [auto_expand_list]
        names = [n[5:] for n in auto_expand_list if n[:5].lower() == 'name:']
        tags  = [p[4:] for p in auto_expand_list if p[:4].lower() == 'tag:']
        self._namematcher = MultiMatcher(names)
        self._tagmatcher = MultiMatcher(tags)

    def check(self, kw):
        if self._namematcher.match(kw.kwname) or self._tagmatcher.match_any(kw.tags):
            self._matched_ids.append(kw.id)

    @property
    def all_matched_ids(self):
        return self._matched_ids

    def __nonzero__(self):
        return bool(self._matcher)
