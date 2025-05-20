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

    def __init__(self, patterns: Sequence[str] = (), ignore: Sequence[str] = "_"):
        self.matcher = MultiMatcher(patterns, ignore)

    def match(self, name: str, full_name: "str|None" = None) -> bool:
        match = self.matcher.match
        return bool(match(name) or full_name and match(full_name))

    def __bool__(self) -> bool:
        return bool(self.matcher)

    def __iter__(self) -> Iterator[str]:
        for matcher in self.matcher:
            yield matcher.pattern
