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

from typing import Iterable, Iterator, Sequence

from robot.utils import MultiMatcher


class NamePatterns(Iterable[str]):

    def __init__(self, patterns: Sequence[str] = (), ignore: Sequence[str] = '_'):
        self.matcher = MultiMatcher(patterns, ignore)

    def match(self, name: str, longname: 'str|None' = None) -> bool:
        return bool(self._match(name) or
                    longname and self._match_longname(longname))

    def _match(self, name: str) -> bool:
        return self.matcher.match(name)

    def _match_longname(self, name: str) -> bool:
        raise NotImplementedError

    def __bool__(self) -> bool:
        return bool(self.matcher)

    def __iter__(self) -> Iterator[str]:
        for matcher in self.matcher:
            yield matcher.pattern


class SuiteNamePatterns(NamePatterns):

    def _match_longname(self, name):
        while '.' in name:
            if self._match(name):
                return True
            name = name.split('.', 1)[1]
        return False


class TestNamePatterns(NamePatterns):

    def _match_longname(self, name):
        return self._match(name)
