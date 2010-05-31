#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

from normalizing import normalize


_match_pattern_tokenizer = re.compile('(\*|\?)')


def eq(str1, str2, ignore=[], caseless=True, spaceless=True):
    str1 = normalize(str1, ignore, caseless, spaceless)
    str2 = normalize(str2, ignore, caseless, spaceless)
    return str1 == str2


def eq_any(str_, str_list, ignore=[], caseless=True, spaceless=True):
    str_ = normalize(str_, ignore, caseless, spaceless)
    for s in str_list:
        if str_ == normalize(s, ignore, caseless, spaceless):
            return True
    return False


def matches(string, pattern, ignore=[], caseless=True, spaceless=True):
    string = normalize(string, ignore, caseless, spaceless)
    pattern = normalize(pattern, ignore, caseless, spaceless)
    regexp = _get_match_regexp(pattern)
    return re.match(regexp, string, re.DOTALL) is not None

def _get_match_regexp(pattern):
    regexp = []
    for token in _match_pattern_tokenizer.split(pattern):
        if token == '*':
            regexp.append('.*')
        elif token == '?':
            regexp.append('.')
        else:
            regexp.append(re.escape(token))
    return '^%s$' % ''.join(regexp)


def matches_any(string, patterns, ignore=[], caseless=True, spaceless=True):
    for pattern in patterns:
        if matches(string, pattern, ignore, caseless, spaceless):
            return True
    return False
