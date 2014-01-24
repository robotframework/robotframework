#  Copyright 2008-2014 Nokia Solutions and Networks
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

"""Visitors can be used to easily travel test suites, test cases and keywords."""

from robot.model import SuiteVisitor


class ResultVisitor(SuiteVisitor):
    """Abstract class to conveniently travel
    :class:`~robot.result.executionresult.Result` objects.

    An implementation of visitor can be given to the visit method of result
    object. This will cause the result object to be traversed and the visitor
    object's ``visit_x``, ``start_x``, and ``end_x`` methods to be called for
    each test suite, test case, and keyword, as well as for errors, statistics,
    and other information in the result object. See methods below for a full
    list of available visitor methods.

    The start and end method are called for each element and their child
    elements. The visitor implementation can override only those that it is
    interested in. If any of the ``start_x`` methods returns False for
    a certain element, its children are not visited.

    If the visitor implements a ``visit_x`` method for element x, then the
    children of that element will not be visited, unless the visitor calls them
    explicitly. For example, if the visitor implements method :meth:`visit_test`,
    the :meth:`start_test`, :meth:`end_test`, :meth:`visit_keyword`,
    :meth:`start_keyword`, and :meth:`end_keyword` methods are not called for
    tests at all.

    See the package documentation for :mod:`a usage example <robot.result>`.
    Visitors are also very widely used internally in Robot Framework. For
    an example, see the source code of :class:`robot.model.tagsetter.TagSetter`.
    """
    def visit_result(self, result):
        if self.start_result(result) is not False:
            result.suite.visit(self)
            result.statistics.visit(self)
            result.errors.visit(self)
            self.end_result(result)

    def start_result(self, result):
        pass

    def end_result(self, result):
        pass

    def visit_statistics(self, stats):
        if self.start_statistics(stats) is not False:
            stats.total.visit(self)
            stats.tags.visit(self)
            stats.suite.visit(self)
            self.end_statistics(stats)

    def start_statistics(self, stats):
        pass

    def end_statistics(self, stats):
        pass

    def visit_total_statistics(self, stats):
        if self.start_total_statistics(stats) is not False:
            for stat in stats:
                stat.visit(self)
            self.end_total_statistics(stats)

    def start_total_statistics(self, stats):
        pass

    def end_total_statistics(self, stats):
        pass

    def visit_tag_statistics(self, stats):
        if self.start_tag_statistics(stats) is not False:
            for stat in stats:
                stat.visit(self)
            self.end_tag_statistics(stats)

    def start_tag_statistics(self, stats):
        pass

    def end_tag_statistics(self, stats):
        pass

    def visit_suite_statistics(self, stats):
        if self.start_suite_statistics(stats) is not False:
            for stat in stats:
                stat.visit(self)
            self.end_suite_statistics(stats)

    def start_suite_statistics(self, stats):
        pass

    def end_suite_statistics(self, suite_stats):
        pass

    def visit_stat(self, stat):
        if self.start_stat(stat) is not False:
            self.end_stat(stat)

    def start_stat(self, stat):
        pass

    def end_stat(self, stat):
        pass

    def visit_errors(self, errors):
        self.start_errors(errors)
        for msg in errors:
            msg.visit(self)
        self.end_errors(errors)

    def start_errors(self, errors):
        pass

    def end_errors(self, errors):
        pass
