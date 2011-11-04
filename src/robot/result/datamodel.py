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

from robot.result.visitor import Visitor

class ResultVisitor(Visitor):

    def start_statistics(self, statistics):
        pass

    def start_total_stats(self, total_stats):
        pass

    def total_stat(self, total_stat):
        pass

    def end_total_stats(self, total_stats):
        pass

    def start_tag_stats(self, tag_stats):
        pass

    def tag_stat(self, tag_stat):
        pass

    def end_tag_stats(self, tag_stats):
        pass

    def start_suite_stats(self, suite_stats):
        pass

    def suite_stat(self, suite_stat):
        pass

    def end_suite_stats(self, suite_stats):
        pass

    def end_statistics(self, statistics):
        pass

    def start_errors(self):
        pass

    def end_errors(self):
        pass


class DatamodelVisitor(ResultVisitor):

    def __init__(self, result):
        self._elements = []
        self._context = Context()
        self._elements.append(ExecutionResultHandler(self._context, result))
        result.visit(self)

    def _start(self, item):
        next = self._elements[-1].start_child_element(item)
        self._elements.append(next)

    start_suite = start_keyword = start_test = _start

    def _end(self, item):
        item_datamodel = self._elements.pop().end_element(item)
        self._elements[-1].add_child_data(item_datamodel)
    end_suite = end_keyword = end_test = _end

    def visit_message(self, msg):
        self._elements[-1].message(msg)

    @property
    def datamodel(self):
        return self._elements[-1].end_element('')
