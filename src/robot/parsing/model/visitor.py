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


class VisitorFinder(object):

    def _find_visitor(self, cls):
        if cls is ast.AST:
            return None
        method = 'visit_' + cls.__name__
        if hasattr(self, method):
            return getattr(self, method)
        for base in cls.__bases__:
            visitor = self._find_visitor(base)
            if visitor:
                return visitor


class ModelVisitor(ast.NodeVisitor, VisitorFinder):

    def visit(self, node):
        visitor = self._find_visitor(type(node)) or self.generic_visit
        visitor(node)


class ModelTransformer(ast.NodeTransformer, VisitorFinder):

    def visit(self, node):
        visitor = self._find_visitor(type(node)) or self.generic_visit
        return visitor(node)
