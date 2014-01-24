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


class CommentCache(object):

    def __init__(self):
        self._comments = []

    def add(self, comment):
        self._comments.append(comment)

    def consume_with(self, function):
        map(function, self._comments)
        self.__init__()


class Comments(object):

    def __init__(self):
        self._comments = []

    def add(self, row):
        if row.comments:
            self._comments.extend(c.strip() for c in row.comments if c.strip())

    @property
    def value(self):
        return self._comments


class Comment(object):

    def __init__(self, comment_data):
        if isinstance(comment_data, basestring):
            comment_data = [comment_data] if comment_data else []
        self._comment = comment_data or []

    def __len__(self):
        return len(self._comment)

    def as_list(self):
        if self._not_commented():
            self._comment[0] = '# ' + self._comment[0]
        return self._comment

    def _not_commented(self):
        return self._comment and self._comment[0] and self._comment[0][0] != '#'
