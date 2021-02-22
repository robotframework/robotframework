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

"""Interface to ease traversing through a test suite structure.

Visitors make it easy to modify test suite structures or to collect information
from them. They work both with the :mod:`executable model <robot.running.model>`
and the :mod:`result model <robot.result.model>`, but the objects passed to
the visitor methods are slightly different depending on the model they are
used with. The main differences are that on the execution side keywords do
not have child keywords nor messages, and that only the result objects have
status related attributes like :attr:`status` and :attr:`starttime`.

This module contains :class:`SuiteVisitor` that implements the core logic to
visit a test suite structure, and the :mod:`~robot.result` package contains
:class:`~robot.result.visitor.ResultVisitor` that supports visiting the whole
test execution result structure. Both of these visitors should be imported
via the :mod:`robot.api` package when used by external code.

Visitor algorithm
-----------------

All suite, test, keyword and message objects have a :meth:`visit` method that
accepts a visitor instance. These methods will then call the correct visitor
method :meth:`~SuiteVisitor.visit_suite`, :meth:`~SuiteVisitor.visit_test`,
:meth:`~SuiteVisitor.visit_keyword` or :meth:`~SuiteVisitor.visit_message`,
depending on the instance where the :meth:`visit` method exists.

The recommended and definitely easiest way to implement a visitor is extending
the :class:`SuiteVisitor` base class. The default implementation of its
:meth:`visit_x` methods take care of traversing child elements of the object
:obj:`x` recursively. A :meth:`visit_x` method first calls a corresponding
:meth:`start_x` method (e.g. :meth:`visit_suite` calls :meth:`start_suite`),
then calls :meth:`visit` for all child objects of the :obj:`x` object, and
finally calls the corresponding :meth:`end_x` method. The default
implementations of :meth:`start_x` and :meth:`end_x` do nothing.

Visitors extending the :class:`SuiteVisitor` can stop visiting at a certain
level either by overriding suitable :meth:`visit_x` method or by returning
an explicit ``False`` from any :meth:`start_x` method.

Examples
--------

The following example visitor modifies the test suite structure it visits.
It could be used, for example, with Robot Framework's ``--prerunmodifier``
option to modify test data before execution.

.. literalinclude:: ../../../doc/api/code_examples/SelectEveryXthTest.py
   :language: python

For more examples it is possible to look at the source code of visitors used
internally by Robot Framework itself. Some good examples are
:class:`~robot.model.tagsetter.TagSetter` and
:mod:`keyword removers <robot.result.keywordremover>`.
"""


class SuiteVisitor(object):
    """Abstract class to ease traversing through the test suite structure.

    See the :mod:`module level <robot.model.visitor>` documentation for more
    information and an example.
    """

    def visit_suite(self, suite):
        """Implements traversing through suites.

        Can be overridden to allow modifying the passed in ``suite`` without
        calling :meth:`start_suite` or :meth:`end_suite` nor visiting child
        suites, tests or keywords (setup and teardown) at all.
        """
        if self.start_suite(suite) is not False:
            suite.setup.visit(self)
            suite.suites.visit(self)
            suite.tests.visit(self)
            suite.teardown.visit(self)
            self.end_suite(suite)

    def start_suite(self, suite):
        """Called when suite starts. Default implementation does nothing.

        Can return explicit ``False`` to stop visiting.
        """
        pass

    def end_suite(self, suite):
        """Called when suite ends. Default implementation does nothing."""
        pass

    def visit_test(self, test):
        """Implements traversing through tests.

        Can be overridden to allow modifying the passed in ``test`` without
        calling :meth:`start_test` or :meth:`end_test` nor visiting keywords.
        """
        if self.start_test(test) is not False:
            test.setup.visit(self)
            test.body.visit(self)
            test.teardown.visit(self)
            self.end_test(test)

    def start_test(self, test):
        """Called when test starts. Default implementation does nothing.

        Can return explicit ``False`` to stop visiting.
        """
        pass

    def end_test(self, test):
        """Called when test ends. Default implementation does nothing."""
        pass

    def visit_keyword(self, kw):
        """Implements traversing through keywords.

        Can be overridden to allow modifying the passed in ``kw`` without
        calling :meth:`start_keyword` or :meth:`end_keyword` nor visiting
        child keywords.
        """
        if self.start_keyword(kw) is not False:
            if hasattr(kw, 'body'):
                kw.body.visit(self)
            kw.teardown.visit(self)
            self.end_keyword(kw)

    def start_keyword(self, keyword):
        """Called when keyword starts. Default implementation does nothing.

        Can return explicit ``False`` to stop visiting.
        """
        pass

    def end_keyword(self, keyword):
        """Called when keyword ends. Default implementation does nothing."""
        pass

    def visit_for(self, for_):
        """Implements traversing through FOR loops.

        Can be overridden to allow modifying the passed in ``for_`` without
        calling :meth:`start_for` or :meth:`end_for` nor visiting body.
        """
        if self.start_for(for_) is not False:
            for_.body.visit(self)
            self.end_for(for_)

    def start_for(self, for_):
        """Called when FOR loop starts. Default implementation does nothing.

        Can return explicit ``False`` to stop visiting.
        """
        pass

    def end_for(self, for_):
        """Called when FOR loop ends. Default implementation does nothing."""
        pass

    def visit_for_iteration(self, iteration):
        """Implements traversing through single FOR loop iteration.

        This is only used with the result side model because on the running side
        there are no iterations.

        Can be overridden to allow modifying the passed in ``iteration`` without
        calling :meth:`start_for_iteration` or :meth:`end_for_iteration` nor visiting
        body.
        """
        if self.start_for_iteration(iteration) is not False:
            iteration.body.visit(self)
            self.end_for_iteration(iteration)

    def start_for_iteration(self, iteration):
        """Called when FOR loop iteration starts. Default implementation does nothing.

        Can return explicit ``False`` to stop visiting.
        """
        pass

    def end_for_iteration(self, iteration):
        """Called when FOR loop iteration ends. Default implementation does nothing."""
        pass

    def visit_if(self, if_):
        """Implements traversing through IF/ELSE structures.

        Notice that ``if_`` does not have any data directly. Actual IF/ELSE branches
        are in its ``body`` and visited using :meth:`visit_if_branch`.

        Can be overridden to allow modifying the passed in ``if_`` without
        calling :meth:`start_if` or :meth:`end_if` nor visiting branches.
        """
        if self.start_if(if_) is not False:
            if_.body.visit(self)
            self.end_if(if_)

    def start_if(self, if_):
        """Called when IF/ELSE structure starts. Default implementation does nothing.

        Can return explicit ``False`` to stop visiting.
        """
        pass

    def end_if(self, if_):
        """Called when IF/ELSE structure ends. Default implementation does nothing."""
        pass

    def visit_if_branch(self, branch):
        """Implements traversing through single IF/ELSE branch.

        Can be overridden to allow modifying the passed in ``branch`` without
        calling :meth:`start_if_branch` or :meth:`end_if_branch` nor visiting body.
        """
        if self.start_if_branch(branch) is not False:
            branch.body.visit(self)
            self.end_if_branch(branch)

    def start_if_branch(self, branch):
        """Called when IF/ELSE branch starts. Default implementation does nothing.

        Can return explicit ``False`` to stop visiting.
        """
        pass

    def end_if_branch(self, branch):
        """Called when IF/ELSE branch ends. Default implementation does nothing."""
        pass

    def visit_message(self, msg):
        """Implements visiting messages.

        Can be overridden to allow modifying the passed in ``msg`` without
        calling :meth:`start_message` or :meth:`end_message`.
        """
        if self.start_message(msg) is not False:
            self.end_message(msg)

    def start_message(self, msg):
        """Called when message starts. Default implementation does nothing.

        Can return explicit ``False`` to stop visiting.
        """
        pass

    def end_message(self, msg):
        """Called when message ends. Default implementation does nothing."""
        pass
