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

from abc import ABC, abstractmethod
from ast import AST, NodeTransformer, NodeVisitor

from .statements import Node


class VisitorFinder(ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__visitor_finder_cache = {}

    @classmethod
    def _find_visitor_class_method(cls, node_cls):
        if node_cls is AST:
            return None
        method_name = "visit_" + node_cls.__name__
        method = getattr(cls, method_name, None)
        if callable(method):
            return method
        if method_name == "visit_Return":
            method = getattr(cls, "visit_ReturnSetting", None)
            if callable(method):
                return method
        for base in node_cls.__bases__:
            method = cls._find_visitor_class_method(base)
            if method:
                return method
        return None

    @classmethod
    def _find_visitor(cls, node_cls):
        if node_cls in cls.__visitor_finder_cache:
            return cls.__visitor_finder_cache[node_cls]
        result = cls.__visitor_finder_cache[node_cls] = cls._find_visitor_class_method(node_cls) or cls.generic_visit
        return result

    @abstractmethod
    def generic_visit(self, node):
        ...


class ModelVisitor(NodeVisitor, VisitorFinder):
    """NodeVisitor that supports matching nodes based on their base classes.

    In other ways identical to the standard `ast.NodeVisitor
    <https://docs.python.org/library/ast.html#ast.NodeVisitor>`__,
    but allows creating ``visit_ClassName`` methods so that the ``ClassName``
    is one of the base classes of the node. For example, this visitor method
    matches all ``Statement`` nodes::

        def visit_Statement(self, node):
            ...
    """

    def visit(self, node: Node) -> None:
        visitor = self._find_visitor(type(node))
        visitor(self, node)


class ModelTransformer(NodeTransformer, VisitorFinder):
    """NodeTransformer that supports matching nodes based on their base classes.

    See :class:`ModelVisitor` for explanation how this is different compared
    to the standard `ast.NodeTransformer
    <https://docs.python.org/library/ast.html#ast.NodeTransformer>`__.
    """

    def visit(self, node: Node) -> "Node|list[Node]|None":
        visitor = self._find_visitor(type(node))
        return visitor(self, node)
