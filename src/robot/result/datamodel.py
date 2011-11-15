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

from robot.reporting.parsingcontext import Context
from robot.result.jsondatamodelhandlers import ExecutionResultHandler, SuiteHandler, KeywordHandler

from robot.result.visitor import ResultVisitor

class DatamodelVisitor(ResultVisitor):

    def __init__(self, result, log_path='NONE', split_log=False):
        self._elements = []
        self._context = Context(log_path=log_path, split_log=split_log)
        self._elements.append(ExecutionResultHandler(self._context, result))

    @property
    def split_results(self):
        return self._context.split_results

    def _start(self, func):
        next = func(self._elements[-1])
        self._elements.append(next)

    def start_suite(self, suite):
        self._start(lambda p: p.start_suite(suite))

    def start_keyword(self, keyword):
        self._start(lambda p: p.start_keyword(keyword))

    def start_test(self, test):
        self._start(lambda p: p.start_test(test))

    def start_errors(self, errors):
        self._start(lambda p: p.start_errors(errors))

    def visit_statistics(self, stats):
        self._start(lambda p: p.visit_statistics(stats))
        self._end(stats)

    def _end(self, item):
        item_datamodel = self._elements.pop().end_element(item)
        self._elements[-1].add_child_data(item_datamodel)

    end_suite = end_keyword = end_test = end_errors = _end

    def end_message(self, msg):
        self._elements[-1].message(msg)

    @property
    def datamodel(self):
        return self._elements[-1].end_element('')
