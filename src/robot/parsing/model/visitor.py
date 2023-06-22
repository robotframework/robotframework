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

import ast

from .statements import Node


class VisitorFinder:

    def _find_visitor(self, cls):
        if cls is ast.AST:
            return None
        method = 'visit_' + cls.__name__
        if hasattr(self, method):
            return getattr(self, method)
        # Forward-compatibility.
        if method == 'visit_Return' and hasattr(self, 'visit_ReturnSetting'):
            return getattr(self, 'visit_ReturnSetting')
        for base in cls.__bases__:
            visitor = self._find_visitor(base)
            if visitor:
                return visitor
        return None


class ModelVisitor(ast.NodeVisitor, VisitorFinder):
    """NodeVisitor that supports matching nodes based on their base classes.

    In other ways identical to the standard `ast.NodeVisitor
    <https://docs.python.org/library/ast.html#ast.NodeVisitor>`__,
    but allows creating ``visit_ClassName`` methods so that the ``ClassName``
    is one of the base classes of the node. For example, this visitor method
    matches all ``Statement`` nodes::

        def visit_Statement(self, node):
            ...
    """

    def visit(self, node: Node):
        visitor = self._find_visitor(type(node)) or self.generic_visit
        visitor(node)


class ModelTransformer(ast.NodeTransformer, VisitorFinder):
    """NodeTransformer that supports matching nodes based on their base classes.

    See :class:`ModelVisitor` for explanation how this is different compared
    to the standard `ast.NodeTransformer
    <https://docs.python.org/library/ast.html#ast.NodeTransformer>`__.
    """

    def visit(self, node: Node):
        visitor = self._find_visitor(type(node)) or self.generic_visit
        return visitor(node)
