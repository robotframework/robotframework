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

from robot.utils import MultiMatcher, py3to2


@py3to2
class _NamePatterns(object):

    def __init__(self, patterns=None):
        self._matcher = MultiMatcher(patterns, ignore='_')

    def match(self, name, longname=None):
        return self._match(name) or longname and self._match_longname(longname)

    def _match(self, name):
        return self._matcher.match(name)

    def _match_longname(self, name):
        raise NotImplementedError

    def __bool__(self):
        return bool(self._matcher)

    def __iter__(self):
        return iter(self._matcher)


class SuiteNamePatterns(_NamePatterns):

    def _match_longname(self, name):
        while '.' in name:
            if self._match(name):
                return True
            name = name.split('.', 1)[1]
        return False


class TestNamePatterns(_NamePatterns):

    def _match_longname(self, name):
        return self._match(name)
