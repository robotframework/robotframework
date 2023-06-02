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
from typing import Iterable, Iterator, Sequence

from .normalizing import normalize
from .robottypes import is_string


def eq(str1: str, str2: str, ignore: Sequence[str] = (), caseless: bool = True,
       spaceless: bool = True) -> bool:
    str1 = normalize(str1, ignore, caseless, spaceless)
    str2 = normalize(str2, ignore, caseless, spaceless)
    return str1 == str2


class Matcher:

    match_2_cache = {}
    """
    https://pypi.org/project/orderedset/
    from collections import OrderedDict
    """

    def __init__(self, pattern: str, ignore: Sequence[str] = (), caseless: bool = True,
                 spaceless: bool = True, regexp: bool = False):
        self.pattern = pattern
        if caseless or spaceless or ignore:
            self._normalize = lambda s: normalize(s, ignore, caseless, spaceless)
        else:
            self._normalize = lambda s: s
        self._normalized_pattern = self._normalize(pattern)
        self._regexp = self._compile(self._normalized_pattern, regexp=regexp)

    def _compile(self, pattern, regexp=False):
        if not regexp:
            pattern = fnmatch.translate(pattern)
        return re.compile(pattern, re.DOTALL)

    def match(self, string: str) -> bool:
        normalized_string = self._normalize(string)
        match_1_cache = self.match_2_cache.get(self._normalized_pattern, {})
        if normalized_string in match_1_cache:
            matching = match_1_cache.pop(normalized_string)
            match_1_cache[normalized_string] = matching
            return matching
        matching = self._regexp.match(normalized_string) is not None
        if 1:#matching:
            if len(match_1_cache) > 32:
                for lru_key in match_1_cache:
                    match_1_cache.pop(lru_key)
                    break
            match_1_cache[normalized_string] = matching
            if len(match_1_cache) <= 1:
                if len(self.match_2_cache) > 32:
                    for lru_key in self.match_2_cache:
                        self.match_2_cache.pop(lru_key)
                        break
                self.match_2_cache[self._normalized_pattern] = match_1_cache
        return matching

    def match_any(self, strings: Iterable[str]) -> bool:
        return any(self.match(s) for s in strings)

    def __bool__(self) -> bool:
        return bool(self._normalize(self.pattern))


class MultiMatcher(Iterable[Matcher]):

    def __init__(self, patterns: Iterable[str] = (), ignore: Sequence[str] = (),
                 caseless: bool = True, spaceless: bool = True,
                 match_if_no_patterns: bool = False, regexp: bool = False):
        self.matchers = [Matcher(pattern, ignore, caseless, spaceless, regexp)
                         for pattern in self._ensure_iterable(patterns)]
        self.match_if_no_patterns = match_if_no_patterns

    def _ensure_iterable(self, patterns):
        if patterns is None:
            return ()
        if is_string(patterns):
            return (patterns,)
        return patterns

    def match(self, string: str) -> bool:
        if self.matchers:
            return any(m.match(string) for m in self.matchers)
        return self.match_if_no_patterns

    def match_any(self, strings: Iterable[str]) -> bool:
        return any(self.match(s) for s in strings)

    def __len__(self) -> int:
        return len(self.matchers)

    def __iter__(self) -> Iterator[Matcher]:
        return iter(self.matchers)
