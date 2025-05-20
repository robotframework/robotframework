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

from typing import Sequence, TYPE_CHECKING

from .visitor import SuiteVisitor

if TYPE_CHECKING:
    from .keyword import Keyword
    from .testcase import TestCase
    from .testsuite import TestSuite


class TagSetter(SuiteVisitor):

    def __init__(
        self,
        add: "Sequence[str]|str" = (),
        remove: "Sequence[str]|str" = (),
    ):
        self.add = add
        self.remove = remove

    def start_suite(self, suite: "TestSuite"):
        return bool(self)

    def visit_test(self, test: "TestCase"):
        test.tags.add(self.add)
        test.tags.remove(self.remove)

    def visit_keyword(self, keyword: "Keyword"):
        pass

    def __bool__(self):
        return bool(self.add or self.remove)
