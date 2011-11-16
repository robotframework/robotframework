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
from .jsondatamodelhandlers import ExecutionResultHandler
from .visitor import ResultVisitor


class JSModelCreator(ResultVisitor):

    def __init__(self, result, log_path='NONE', split_log=False):
        self._context = Context(log_path=log_path, split_log=split_log)
        self._elements = [ExecutionResultHandler(self._context, result)]

    @property
    def datamodel(self):
        #TODO: End element should not require argument in this case
        return self._top.end_element(None)

    @property
    def _top(self):
        return self._elements[-1]

    def _push(self, element):
        self._elements.append(element)

    def _pop(self):
        return self._elements.pop()

    @property
    def split_results(self):
        return self._context.split_results

    def start_suite(self, suite):
        self._push(self._top.start_suite(suite))

    def start_keyword(self, keyword):
        self._push(self._top.start_keyword(keyword))

    def start_test(self, test):
        self._push(self._top.start_test(test))

    def start_errors(self, errors):
        self._push(self._top.start_errors(errors))

    def visit_statistics(self, stats):
        self._push(self._top.visit_statistics(stats))
        self._end(stats)

    #TODO: end_elements should also work in similar as starts
    def _end(self, item):
        submodel = self._pop().end_element(item)
        self._top.add_child_data(submodel)

    end_suite = end_keyword = end_test = end_errors = _end

    def end_message(self, msg):
        self._top.message(msg)
