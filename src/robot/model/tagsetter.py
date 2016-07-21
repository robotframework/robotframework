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

from robot.utils import py2to3

from .visitor import SuiteVisitor


@py2to3
class TagSetter(SuiteVisitor):

    def __init__(self, add=None, remove=None):
        self.add = add
        self.remove = remove

    def start_suite(self, suite):
        return bool(self)

    def visit_test(self, test):
        test.tags.add(self.add)
        test.tags.remove(self.remove)

    def visit_keyword(self, keyword):
        pass

    def __nonzero__(self):
        return bool(self.add or self.remove)
