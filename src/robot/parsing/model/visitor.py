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

from ast import NodeTransformer, NodeVisitor
from typing import Callable

from .statements import Node

# Unbound method and thus needs `NodeVisitor` as `self`.
VisitorMethod = Callable[[NodeVisitor, Node], "None|Node|list[Node]"]


class VisitorFinder:
    __visitor_cache: "dict[type[Node], VisitorMethod]"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__visitor_cache = {}

    @classmethod
    def _find_visitor(cls, node_cls: "type[Node]") -> VisitorMethod:
        if node_cls not in cls.__visitor_cache:
            visitor = cls._find_visitor_from_class(node_cls)
            cls.__visitor_cache[node_cls] = visitor or cls.generic_visit
        return cls.__visitor_cache[node_cls]

    @classmethod
    def _find_visitor_from_class(cls, node_cls: "type[Node]") -> "VisitorMethod|None":
        method_name = "visit_" + node_cls.__name__
        method = getattr(cls, method_name, None)
        if callable(method):
            return method
        if method_name in ("visit_TestTags", "visit_Return"):
            method = cls._backwards_compatibility(method_name)
            if callable(method):
                return method
        for base in node_cls.__bases__:
            if issubclass(base, Node):
                method = cls._find_visitor_from_class(base)
                if method:
                    return method
        return None

    @classmethod
    def _backwards_compatibility(cls, method_name):
        name = {
            "visit_TestTags": "visit_ForceTags",
            "visit_Return": "visit_ReturnStatement",
        }[method_name]
        return getattr(cls, name, None)

    def generic_visit(self, node: Node) -> "None|Node|list[Node]":
        raise NotImplementedError


class ModelVisitor(NodeVisitor, VisitorFinder):
    """NodeVisitor that supports matching nodes based on their base classes.

    The biggest difference compared to the standard `ast.NodeVisitor
    <https://docs.python.org/library/ast.html#ast.NodeVisitor>`__,
    is that this class allows creating ``visit_ClassName`` methods so that
    the ``ClassName`` is one of the base classes of the node. For example,
    the following visitor method matches all node classes that extend
    ``Statement``::

        def visit_Statement(self, node):
            ...

    Another difference is that visitor methods are cached for performance
    reasons. This means that dynamically adding ``visit_Something`` methods
    does not work.
    """

    def visit(self, node: Node) -> None:
        visitor_method = self._find_visitor(type(node))
        visitor_method(self, node)


class ModelTransformer(NodeTransformer, VisitorFinder):
    """NodeTransformer that supports matching nodes based on their base classes.

    See :class:`ModelVisitor` for explanation how this is different compared
    to the standard `ast.NodeTransformer
    <https://docs.python.org/library/ast.html#ast.NodeTransformer>`__.
    """

    def visit(self, node: Node) -> "None|Node|list[Node]":
        visitor_method = self._find_visitor(type(node))
        return visitor_method(self, node)
