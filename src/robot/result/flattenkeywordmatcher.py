#  Copyright 2008-2015 Nokia Solutions and Networks
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


def validate_flatten_keyword(options):
    for opt in options:
        low = opt.lower()
        if not (low in ('for', 'foritem') or
                low.startswith('name:') or
                low.startswith('tag:')):
            raise DataError("Expected 'FOR', 'FORITEM', 'TAG:<pattern>', or "
                            "'NAME:<pattern>' but got '%s'." % opt)


@py2to3
class FlattenByTypeMatcher(object):

    def __init__(self, flatten):
        if not is_list_like(flatten):
            flatten = [flatten]
        flatten = [f.lower() for f in flatten]
        self._types = [f for f in flatten if f in ('for', 'foritem')]

    def match(self, kwtype):
        return kwtype in self._types

    def __nonzero__(self):
        return bool(self._types)


@py2to3
class FlattenByNameMatcher(object):

    def __init__(self, flatten):
        if not is_list_like(flatten):
            flatten = [flatten]
        names = [n[5:] for n in flatten if n[:5].lower() == 'name:']
        self._matcher = MultiMatcher(names)

    def match(self, kwname, libname=None):
        name = '%s.%s' % (libname, kwname) if libname else kwname
        return self._matcher.match(name)

    def __nonzero__(self):
        return bool(self._matcher)


@py2to3
class FlattenByTagMatcher(object):

    def __init__(self, flatten):
        if not is_list_like(flatten):
            flatten = [flatten]
        patterns = [p[4:] for p in flatten if p[:4].lower() == 'tag:']
        self._matcher = TagPatterns(patterns)

    def match(self, kwtags):
        return self._matcher.match(kwtags)

    def __nonzero__(self):
        return bool(self._matcher)
