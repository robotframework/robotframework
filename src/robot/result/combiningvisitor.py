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

def _create_method(method_name):
    def delegate_call(self, item):
        for visitor in self._visitors:
            getattr(visitor, method_name)(item)
    setattr(CombiningVisitor, method_name, delegate_call)

for method_name in (pre+'_'+post
                    for pre in ('start', 'end') \
                    for post in ('suite', 'test', 'keyword', 'message', 'errors')):
    _create_method(method_name)
_create_method('visit_statistics')


class RemovingVisitor(ResultVisitor):

    def end_keyword(self, keyword):
        keyword.keywords = []
        keyword.messaged = []

    def end_test(self, test):
        test.keywords = []

    def end_suite(self, suite):
        suite.suites = []
        suite.keywords = []
        suite.tests = []
