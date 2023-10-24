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
from typing import Any, Callable, Dict, Optional, Type, Union

from .statements import Node


class _NotSet:
    pass


class VisitorFinder:
    __NOT_SET = _NotSet()
    __cls_cache: Dict[Type[Any], Union[Callable[..., Any], None, _NotSet]]

    def __new__(cls, *_args: Any, **_kwargs: Any):  # type: ignore[no-untyped-def]
        # create cache on class level to avoid creating it for each instance
        cls.__cls_cache = {}
        return super().__new__(cls)

    @classmethod
    def __find_visitor(cls, node_cls: Type[Any]) -> Optional[Callable[..., Any]]:
        if node_cls is ast.AST:
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
            method = cls._find_visitor(base)
            if method:
                return method
        return None

    @classmethod
    def _find_visitor(cls, node_cls: Type[Any]) -> Optional[Callable[..., Any]]:
        result = cls.__cls_cache.get(node_cls, cls.__NOT_SET)
        if result is cls.__NOT_SET:
            result = cls.__cls_cache[node_cls] = cls.__find_visitor(node_cls)
        return result  # type: ignore[return-value]


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

    def visit(self, node: Node) -> None:
        visitor = self._find_visitor(type(node)) or self.__class__.generic_visit
        visitor(self, node)


class ModelTransformer(ast.NodeTransformer, VisitorFinder):
    """NodeTransformer that supports matching nodes based on their base classes.

    See :class:`ModelVisitor` for explanation how this is different compared
    to the standard `ast.NodeTransformer
    <https://docs.python.org/library/ast.html#ast.NodeTransformer>`__.
    """

    def visit(self, node: Node) -> Node:
        visitor = self._find_visitor(type(node)) or self.__class__.generic_visit
        return visitor(self, node)
