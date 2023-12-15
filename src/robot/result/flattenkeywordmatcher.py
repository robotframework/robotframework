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
from robot.model import TagPatterns, SuiteVisitor
from robot.utils import html_escape, MultiMatcher

from .model import Keyword


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


def create_flatten_message(original):
    if not original:
        start = ''
    elif original.startswith('*HTML*'):
        start = original[6:].strip() + '<hr>'
    else:
        start = html_escape(original) + '<hr>'
    return f'*HTML* {start}<span class="robot-note">Content flattened.</span>'


class FlattenByTypeMatcher:

    def __init__(self, flatten):
        if isinstance(flatten, str):
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
        if isinstance(flatten, str):
            flatten = [flatten]
        names = [n[5:] for n in flatten if n[:5].lower() == 'name:']
        self._matcher = MultiMatcher(names)

    def match(self, name, owner=None):
        name = f'{owner}.{name}' if owner else name
        return self._matcher.match(name)

    def __bool__(self):
        return bool(self._matcher)


class FlattenByTagMatcher:

    def __init__(self, flatten):
        if isinstance(flatten, str):
            flatten = [flatten]
        patterns = [p[4:] for p in flatten if p[:4].lower() == 'tag:']
        self._matcher = TagPatterns(patterns)

    def match(self, tags):
        return self._matcher.match(tags)

    def __bool__(self):
        return bool(self._matcher)


class FlattenByTags(SuiteVisitor):

    def __init__(self, flatten):
        if isinstance(flatten, str):
            flatten = [flatten]
        patterns = [p[4:] for p in flatten if p[:4].lower() == 'tag:']
        self.matcher = TagPatterns(patterns)

    def start_suite(self, suite):
        return bool(self.matcher)

    def start_keyword(self, keyword: Keyword):
        if self.matcher.match(keyword.tags):
            keyword.message = create_flatten_message(keyword.message)
            keyword.body = MessageFinder(keyword).messages


class MessageFinder(SuiteVisitor):

    def __init__(self, keyword: Keyword):
        self.messages = []
        keyword.visit(self)

    def visit_message(self, message):
        self.messages.append(message)
