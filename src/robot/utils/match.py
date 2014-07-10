#  Copyright 2008-2014 Nokia Solutions and Networks
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


def eq(str1, str2, ignore=(), caseless=True, spaceless=True):
    str1 = normalize(str1, ignore, caseless, spaceless)
    str2 = normalize(str2, ignore, caseless, spaceless)
    return str1 == str2


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

    def match_any(self, strings):
        return any(self.match(s) for s in strings)


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


def contains(pattern, iterable, case_insensitive=False):
    """Check for matches to a pattern or value in an iterable.

    If pattern is a string beginning with 'glob=' or 'regexp=', treat the rest
    of the string as a glob or regexp pattern to match.

    If case_insensitive is True, ignore case when matching.

    Glob and regexp searches only match against strings.
    """
    return bool(count_matches(pattern, iterable, case_insensitive))


def count_matches(pattern, iterable, case_insensitive=False):
    """Count matches to a pattern or value in an iterable.

    If pattern is a string beginning with 'glob=' or 'regexp=', treat the rest
    of the string as a glob or regexp pattern to match.

    If case_insensitive is True, ignore case when matching.

    Glob and regexp searches only match against strings.
    """
    if not iterable:
        return 0
    regexp = False
    try:
        if pattern.lower().startswith('glob='):
            # translate glob pattern to re pattern
            pattern = fnmatch.translate(pattern[5:])
            regexp = True
        elif pattern.lower().startswith('regexp='):
            pattern = pattern[7:]
            regexp = True
    except AttributeError:
        # calling lower() on a non-string raises AttributeError
        pass

    if regexp:
        flags = 0
        if case_insensitive:
            flags = re.IGNORECASE
        condition = [bool(re.match(pattern, item, flags))
                     if isinstance(item, basestring) else pattern == item
                     for item in iterable]
    else:
        if case_insensitive and isinstance(pattern, basestring):
            condition = [pattern.lower() == item.lower()
                         if isinstance(item, basestring) else pattern == item
                         for item in iterable]
        else:
            condition = [pattern == item for item in iterable]
    if not condition or not any(condition):
        # fall back to most basic logic if nothing else works
        if pattern in iterable:
            # try to convert uncountable iterables to lists
            if not hasattr(iterable, 'count'):
                try:
                    iterable = list(iterable)
                except AttributeError:
                    pass
            # the 'or 1' workaround is required for NormalizedDict, since the
            # list of keys of a NormalizedDict is not normalized, while
            # NormalizedDict.__iter__ returns normalized keys
            return iterable.count(pattern) or 1
    return condition.count(True)
