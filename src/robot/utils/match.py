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
import fnmatch
from functools import partial

from .normalizing import normalize
from .robottypes import is_string


def eq(str1, str2, ignore=(), caseless=True, spaceless=True):
    str1 = normalize(str1, ignore, caseless, spaceless)
    str2 = normalize(str2, ignore, caseless, spaceless)
    return str1 == str2


class Matcher:

    def __init__(self, pattern, ignore=(), caseless=True, spaceless=True, regexp=False):
        self.pattern = pattern
        self._normalize = partial(normalize, ignore=ignore, caseless=caseless,
                                  spaceless=spaceless)
        self._regexp = self._compile(self._normalize(pattern), regexp=regexp)

    def _compile(self, pattern, regexp=False):
        if not regexp:
            pattern = fnmatch.translate(pattern)
        return re.compile(pattern, re.DOTALL)

    def match(self, string):
        return self._regexp.match(self._normalize(string)) is not None

    def match_any(self, strings):
        return any(self.match(s) for s in strings)

    def __bool__(self):
        return bool(self._normalize(self.pattern))


class MultiMatcher:

    def __init__(self, patterns=None, ignore=(), caseless=True, spaceless=True,
                 match_if_no_patterns=False, regexp=False):
        self._matchers = [Matcher(pattern, ignore, caseless, spaceless, regexp)
                          for pattern in self._ensure_list(patterns)]
        self._match_if_no_patterns = match_if_no_patterns

    def _ensure_list(self, patterns):
        if patterns is None:
            return []
        if is_string(patterns):
            return [patterns]
        return patterns

    def match(self, string):
        if self._matchers:
            return any(m.match(string) for m in self._matchers)
        return self._match_if_no_patterns

    def match_any(self, strings):
        return any(self.match(s) for s in strings)

    def __len__(self):
        return len(self._matchers)

    def __iter__(self):
        for matcher in self._matchers:
            yield matcher.pattern
