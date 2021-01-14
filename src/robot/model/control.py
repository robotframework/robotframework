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

from robot.utils import setter, py3to2

from .body import Body, BodyItem
from .keyword import Keywords


@py3to2
@Body.register
class For(BodyItem):
    __slots__ = ['variables', 'flavor', 'values']
    type = BodyItem.FOR_TYPE
    body_class = Body

    def __init__(self, variables=(), flavor='IN', values=(), parent=None):
        self.variables = variables
        self.flavor = flavor
        self.values = values
        self.parent = parent
        self.body = None

    @setter
    def body(self, body):
        return self.body_class(self, body)

    @property
    def keywords(self):
        """Deprecated since Robot Framework 4.0. Use :attr:`body` instead."""
        return Keywords(self, self.body)

    @keywords.setter
    def keywords(self, keywords):
        Keywords.raise_deprecation_error()

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def visit(self, visitor):
        visitor.visit_for(self)

    def __str__(self):
        variables = '    '.join(self.variables)
        values = '    '.join(self.values)
        return u'FOR    %s    %s    %s' % (variables, self.flavor, values)


@py3to2
@Body.register
class If(BodyItem):
    __slots__ = ['condition', '_orelse']
    body_class = Body
    inactive = object()

    def __init__(self, condition=None, parent=None):
        self.condition = condition
        self.parent = parent
        self.body = None
        self._orelse = None

    @setter
    def body(self, body):
        return self.body_class(self, body)

    @property     # Cannot use @setter because it would create orelses recursively.
    def orelse(self):
        if self._orelse is None and self:
            self._orelse = type(self)(condition=self.inactive, parent=self)
        return self._orelse

    @orelse.setter
    def orelse(self, orelse):
        if orelse is None:
            self._orelse = None
        elif not isinstance(orelse, type(self)):
            raise TypeError("Only %s objects accepted, got %s."
                            % (type(self).__name__, type(orelse).__name__))
        else:
            orelse.parent = self
            self._orelse = orelse

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    @property
    def type(self):
        if self.condition is self.inactive:
            return None
        if not isinstance(self.parent, If):
            return self.IF_TYPE
        if self.condition:
            return self.ELSE_IF_TYPE
        return self.ELSE_TYPE

    def visit(self, visitor):
        if self:
            visitor.visit_if(self)

    def __str__(self):
        if self.condition is self.inactive:
            return u'INACTIVE'
        if not isinstance(self.parent, If):
            return u'IF    %s' % self.condition
        if self.condition:
            return u'ELSE IF    %s' % self.condition
        return u'ELSE'

    def __bool__(self):
        return self.condition is not self.inactive
