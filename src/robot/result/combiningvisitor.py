#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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
from robot.result.visitor import ResultVisitor

class CombiningVisitor(ResultVisitor):

    def __init__(self, *visitors):
        self._visitors = visitors
        for name in dir(self):
            if name.startswith('start') or name.startswith('end'):
                self._create_delegating_method(name)
        self._create_delegating_method('visit_statistics')

    def _create_delegating_method(self, method_name):
        setattr(self, method_name, self._delegate_call(method_name))

    def _delegate_call(self, method_name):
        def delegator(item):
            for visitor in self._visitors:
                getattr(visitor, method_name)(item)
        return delegator


class KeywordRemovingVisitor(ResultVisitor):

    def end_keyword(self, keyword):
        keyword.keywords = []

    def end_test(self, test):
        test.keywords = []

    def end_suite(self, suite):
        suite.keywords = []
