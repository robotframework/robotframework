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

import re
from functools import partial

from .normalizing import normalize


def eq(str1, str2, ignore=(), caseless=True, spaceless=True):
    str1 = normalize(str1, ignore, caseless, spaceless)
    str2 = normalize(str2, ignore, caseless, spaceless)
    return str1 == str2


# TODO: Remove matches and matches_any in 2.8.
# They aren't used much in 2.7 anymore but don't want to remove them after RC.

def matches(string, pattern, ignore=(), caseless=True, spaceless=True):
    """Deprecated!! Use Matcher instead."""
    return Matcher(pattern, ignore, caseless, spaceless).match(string)


def matches_any(string, patterns, ignore=(), caseless=True, spaceless=True):
    """Deprecated!! Use MultiMatcher instead."""
    matcher = MultiMatcher(patterns, ignore, caseless, spaceless)
    return matcher.match(string)


class Matcher(object):
    _pattern_tokenizer = re.compile('(\*|\?)')
    _wildcards = {'*': '.*', '?': '.'}

    def __init__(self, pattern, ignore=(), caseless=True, spaceless=True):
        self.pattern = pattern
        self._normalize = partial(normalize, ignore=ignore, caseless=caseless,
                                  spaceless=spaceless)
        self._regexp = self._get_and_compile_regexp(self._normalize(pattern))

    def _get_and_compile_regexp(self, pattern):
        pattern = '^%s$' % ''.join(self._yield_regexp(pattern))
        return re.compile(pattern, re.DOTALL)

    def _yield_regexp(self, pattern):
        for token in self._pattern_tokenizer.split(pattern):
            if token in self._wildcards:
                yield self._wildcards[token]
            else:
                yield re.escape(token)

    def match(self, string):
        return self._regexp.match(self._normalize(string)) is not None


class MultiMatcher(object):

    def __init__(self, patterns=None, ignore=(), caseless=True, spaceless=True,
                 match_if_no_patterns=False):
        self._matchers = [Matcher(pattern, ignore, caseless, spaceless)
                          for pattern in self._ensure_list(patterns)]
        self._match_if_no_patterns = match_if_no_patterns

    def _ensure_list(self, patterns):
        if patterns is None:
            return []
        if isinstance(patterns, basestring):
            return  [patterns]
        return patterns

    def match(self, string):
        if self._matchers:
            return any(m.match(string) for m in self._matchers)
        return self._match_if_no_patterns

    def __len__(self):
        return len(self._matchers)

    def __iter__(self):
        for matcher in self._matchers:
            yield matcher.pattern
