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
from functools import partial

from .compat import py2to3
from .normalizing import normalize
from .platform import PY3
from .robottypes import is_string


def eq(str1, str2, ignore=(), caseless=True, spaceless=True):
    str1 = normalize(str1, ignore, caseless, spaceless)
    str2 = normalize(str2, ignore, caseless, spaceless)
    return str1 == str2


@py2to3
class Matcher(object):
    _wildcards = {'*': '.*', '?': '.', b'*': b'.*', b'?': b'.'}

    def __init__(self, pattern, ignore=(), caseless=True, spaceless=True,
                 regexp=False):
        self.pattern = pattern
        self._normalize = partial(normalize, ignore=ignore, caseless=caseless,
                                  spaceless=spaceless)
        self._regexp = self._get_and_compile_regexp(self._normalize(pattern),
                                                    regexp=regexp)

    def _get_and_compile_regexp(self, pattern, regexp=False):
        if not regexp:
            pattern = self._glob_pattern_to_regexp(pattern)
        return re.compile(pattern, re.DOTALL)

    def _glob_pattern_to_regexp(self, pattern):
        if PY3 and isinstance(pattern, bytes):
            tokenizer = re.compile(b'(\*|\?)')
            start, end, empty = b'^', b'$', b''
        else:
            tokenizer = re.compile('(\*|\?)')
            start, end, empty = '^', '$', ''
        tokens = self._tokenize_glob_pattern(tokenizer, pattern)
        return start + empty.join(tokens) + end

    def _tokenize_glob_pattern(self, tokenizer, pattern):
        for token in tokenizer.split(pattern):
            if token in self._wildcards:
                yield self._wildcards[token]
            else:
                yield re.escape(token)

    def match(self, string):
        return self._regexp.match(self._normalize(string)) is not None

    def match_any(self, strings):
        return any(self.match(s) for s in strings)

    def __nonzero__(self):
        return bool(self._normalize(self.pattern))


class MultiMatcher(object):

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
