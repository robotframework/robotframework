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

from abc import ABC
from ast import AST
from collections import defaultdict
from typing import Any, Callable, Generic, Iterator, TypeVar

from ...utils.notset import NOT_SET, NotSet
from .statements import Node

TVisitorResult = TypeVar("TVisitorResult")


class VisitorFinder(ABC, Generic[TVisitorResult]):
    __visitor_finder_cache: "dict[type[Any], Callable[[Node], Any]|None|NotSet]"
    __default_visitor_method: "Callable[..., TVisitorResult]"

    def __init_subclass__(cls, default_visitor_name: str = "generic_visit", **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.__visitor_finder_cache = defaultdict(lambda: NOT_SET)
        cls.__default_visitor_method = getattr(cls, default_visitor_name)

    @classmethod
    def _find_visitor_class_method(cls, node_cls: "type[Any]") -> "Callable[..., TVisitorResult]|None":
        if node_cls is AST:
            return None
        method_name = "visit_" + node_cls.__name__
        method = getattr(cls, method_name, None)
        if callable(method):
            return method  # type: ignore[no-any-return]
        if method_name == "visit_Return":
            method = getattr(cls, "visit_ReturnSetting", None)
            if callable(method):
                return method  # type: ignore[no-any-return]
        for base in node_cls.__bases__:
            method = cls._find_visitor_class_method(base)
            if method:
                return method
        return None

    @classmethod
    def _find_visitor(cls, node_cls: "type[Any]") -> Callable[..., TVisitorResult]:
        result = cls.__visitor_finder_cache[node_cls]
        if result is NOT_SET:
            result = cls.__visitor_finder_cache[node_cls] = cls._find_visitor_class_method(node_cls)
        return result or cls.__default_visitor_method  # type: ignore[return-value]


def _iter_field_values(node: Node) -> "Iterator[Node|list[Node]|None]":
    for field in node._fields:
        try:
            yield getattr(node, field)
        except AttributeError:
            pass


def iter_fields(node: Node) -> "Iterator[tuple[str, Node|list[Node]|None]]":
    for field in node._fields:
        try:
            yield field, getattr(node, field)
        except AttributeError:
            pass


class ModelVisitor(VisitorFinder[None]):
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

    def generic_visit(self, node: Node) -> None:
        for value in _iter_field_values(node):
            if value is None:
                continue
            if isinstance(value, list):
                for item in value:
                    self.visit(item)
            else:
                self.visit(value)


class ModelTransformer(VisitorFinder["Node|list[Node]|None"]):
    """NodeTransformer that supports matching nodes based on their base classes.

    See :class:`ModelVisitor` for explanation how this is different compared
    to the standard `ast.NodeTransformer
    <https://docs.python.org/library/ast.html#ast.NodeTransformer>`__.
    """

    def visit(self, node: Node) -> "Node|list[Node]|None":
        visitor = self._find_visitor(type(node))
        return visitor(self, node)

    def generic_visit(self, node: Node) -> "Node|list[Node]|None":
        for field, old_value in iter_fields(node):
            if old_value is None:
                continue
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    new_value = self.visit(value)
                    if new_value is None:
                        continue
                    if isinstance(new_value, list):
                        new_values.extend(new_value)
                        continue
                    new_values.append(new_value)
                old_value[:] = new_values
            else:
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)

        return node
