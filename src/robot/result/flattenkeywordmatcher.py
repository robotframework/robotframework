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
from robot.utils import MultiMatcher, is_list_like


def validate_flatten_keyword(options):
    for opt in options:
        low = opt.lower()
        # TODO: Deprecate 'foritem' in RF 6.1!
        if low == 'foritem':
            low = 'iteration'
        if not (low in ('for', 'while', 'iteration') or
                low.startswith('name:') or
                low.startswith('tag:')):
            raise DataError(f"Expected 'FOR', 'WHILE', 'ITERATION', 'TAG:<pattern>' or "
                            f"'NAME:<pattern>', got '{opt}'.")


class FlattenByTypeMatcher:

    def __init__(self, flatten):
        if not is_list_like(flatten):
            flatten = [flatten]
        flatten = [f.lower() for f in flatten]
        self.types = set()
        if 'for' in flatten:
            self.types.add('for')
        if 'while' in flatten:
            self.types.add('while')
        if 'iteration' in flatten or 'foritem' in flatten:
            self.types.add('iter')

    def match(self, tag):
        return tag in self.types

    def __bool__(self):
        return bool(self.types)


class FlattenByNameMatcher:

    def __init__(self, flatten):
        if not is_list_like(flatten):
            flatten = [flatten]
        names = [n[5:] for n in flatten if n[:5].lower() == 'name:']
        self._matcher = MultiMatcher(names)

    def match(self, kwname, libname=None):
        name = '%s.%s' % (libname, kwname) if libname else kwname
        return self._matcher.match(name)

    def __bool__(self):
        return bool(self._matcher)


class FlattenByTagMatcher:

    def __init__(self, flatten):
        if not is_list_like(flatten):
            flatten = [flatten]
        patterns = [p[4:] for p in flatten if p[:4].lower() == 'tag:']
        self._matcher = TagPatterns(patterns)

    def match(self, kwtags):
        return self._matcher.match(kwtags)

    def __bool__(self):
        return bool(self._matcher)
