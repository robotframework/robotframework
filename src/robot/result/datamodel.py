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

    def __init__(self, log_path='NONE', split_log=False):
        self._context = Context(log_path=log_path, split_log=split_log)
        self._handlers = [ExecutionResultHandler(self._context)]
        self._datamodel = None

    @property
    def datamodel(self):
        if self._datamodel is None:
            self._datamodel = self._build()
        return self._datamodel

    @property
    def split_results(self):
        return self._context.split_results

    @property
    def _top(self):
        return self._handlers[-1]

    def _push(self, handler):
        self._handlers.append(handler)

    def _build(self, item=None):
        return self._handlers.pop().build(item)

    def start_suite(self, suite):
        self._push(self._top.suite_handler())

    def end_suite(self, suite):
        model = self._build(suite)
        self._top.add_suite(model)

    def start_test(self, test):
        self._push(self._top.test_handler())

    def end_test(self, test):
        model = self._build(test)
        self._top.add_test(model)

    def start_keyword(self, kw):
        self._push(self._top.keyword_handler())

    def end_keyword(self, kw):
        model = self._build(kw)
        self._top.add_keyword(model)

    def start_message(self, msg):
        self._push(self._top.message_handler())

    def end_message(self, msg):
        model = self._build(msg)
        self._top.add_message(model)

    def start_errors(self, errors):
        self._push(self._top.errors_handler())

    def end_errors(self, errors):
        model = self._build(errors)
        self._top.add_errors(model)

    def visit_statistics(self, stats):
        self._top.visit_statistics(stats)
