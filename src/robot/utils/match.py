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

import re
from functools import partial

from .normalizing import normalize


def eq(str1, str2, ignore=(), caseless=True, spaceless=True):
    str1 = normalize(str1, ignore, caseless, spaceless)
    str2 = normalize(str2, ignore, caseless, spaceless)
    return str1 == str2


def matches(string, pattern, ignore=(), caseless=True, spaceless=True):
    return Matcher(pattern, ignore, caseless, spaceless).match(string)


# TODO: matches_any should be removed and any(utils.match(...) for p in patterns)
# used instead. Currently mainly used in robot.common.model and can be removed
# after that module is nuked.
def matches_any(string, patterns, ignore=(), caseless=True, spaceless=True):
    for pattern in patterns:
        if matches(string, pattern, ignore, caseless, spaceless):
            return True
    return False


class Matcher(object):
    _match_pattern_tokenizer = re.compile('(\*|\?)')
    _wildcards = {'*': '.*', '?': '.'}

    def __init__(self, pattern, ignore=(), caseless=True, spaceless=True):
        self.pattern = pattern
        self._normalize = partial(normalize, ignore=ignore, caseless=caseless,
                                  spaceless=spaceless)
        self._regexp = self._get_and_compile_regexp(self._normalize(pattern))

    def _get_and_compile_regexp(self, pattern):
        pattern = '^%s$' % ''.join(self._get_regexp(pattern))
        return re.compile(pattern, re.DOTALL)

    def _get_regexp(self, pattern):
        for token in self._match_pattern_tokenizer.split(pattern):
            if token in self._wildcards:
                yield self._wildcards[token]
            else:
                yield re.escape(token)

    def match(self, string):
        return self._regexp.match(self._normalize(string)) is not None


class MultiMatcher(object):

    def __init__(self, patterns=None, ignore=(), caseless=True, spaceless=True,
                 match_if_no_patterns=True):
        self._matchers = [Matcher(p, ignore, caseless, spaceless)
                          for p in patterns or []]
        self._match_if_no_patterns = match_if_no_patterns

    def match(self, string):
        if not self._matchers and self._match_if_no_patterns:
            return True
        return any(m.match(string) for m in self._matchers)
