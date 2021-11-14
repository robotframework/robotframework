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

from robot.utils import setter

from .body import Body, BodyItem, IfBranches, ExceptHandlers
from .keyword import Keywords


class Block(BodyItem):
    body_class = Body
    __slots__ = ['type', 'parent']
    repr_args = ('type',)

    def __init__(self, type, parent=None):
        self.type = type
        self.parent = parent
        self.body = None

    @setter
    def body(self, body):
        return self.body_class(self, body)


@Body.register
class For(BodyItem):
    type = BodyItem.FOR
    body_class = Body
    repr_args = ('variables', 'flavor', 'values')
    __slots__ = ['variables', 'flavor', 'values']

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

    def visit(self, visitor):
        visitor.visit_for(self)

    def __str__(self):
        variables = '    '.join(self.variables)
        values = '    '.join(self.values)
        return 'FOR    %s    %s    %s' % (variables, self.flavor, values)


@Body.register
class If(BodyItem):
    """IF/ELSE structure root. Branches are stored in :attr:`body`."""
    type = BodyItem.IF_ELSE_ROOT
    body_class = IfBranches
    __slots__ = ['parent']

    def __init__(self, parent=None):
        self.parent = parent
        self.body = None

    @setter
    def body(self, body):
        return self.body_class(self, body)

    @property
    def id(self):
        """Root IF/ELSE id is always ``None``."""
        return None

    def visit(self, visitor):
        visitor.visit_if(self)


@IfBranches.register
class IfBranch(BodyItem):
    body_class = Body
    repr_args = ('type', 'condition')
    __slots__ = ['type', 'condition']

    def __init__(self, type=BodyItem.IF, condition=None, parent=None):
        self.type = type
        self.condition = condition
        self.parent = parent
        self.body = None

    @setter
    def body(self, body):
        return self.body_class(self, body)

    @property
    def id(self):
        """Branch id omits the root IF/ELSE object from the parent id part."""
        if not self.parent:
            return 'k1'
        index = self.parent.body.index(self) + 1
        if not self.parent.parent:
            return 'k%d' % index
        return '%s-k%d' % (self.parent.parent.id, index)

    def __str__(self):
        if self.type == self.IF:
            return 'IF    %s' % self.condition
        if self.type == self.ELSE_IF:
            return 'ELSE IF    %s' % self.condition
        return 'ELSE'

    def visit(self, visitor):
        visitor.visit_if_branch(self)


@Body.register
class Try(BodyItem):
    type = BodyItem.TRY_EXCEPT_ROOT
    try_class = Block
    handlers_class = ExceptHandlers
    else_class = Block
    __slots__ = ['parent', 'try_block', 'else_block']

    def __init__(self, parent=None):
        self.parent = parent
        self.try_block = self.try_class(BodyItem.TRY, parent=self)
        self.handlers = None
        self.else_block = self.else_class(BodyItem.TRY_ELSE, parent=self)

    @setter
    def handlers(self, handlers):
        return self.handlers_class(self, handlers)

    @property
    def id(self):
        """Root TRY/EXCEPT id is always ``None``."""
        return None

    def visit(self, visitor):
        visitor.visit_try(self)


@ExceptHandlers.register
class Except(BodyItem):
    type = BodyItem.EXCEPT
    body_class = Body
    repr_args = ('type', 'pattern')
    __slots__ = ['pattern']

    def __init__(self, pattern=None, parent=None):
        self.pattern = pattern
        self.parent = parent
        self.body = None

    @setter
    def body(self, body):
        return self.body_class(self, body)

    @property
    def id(self):
        """Branch id omits the root IF/ELSE object from the parent id part."""
        if not self.parent:
            return 'k1'
        index = self.parent.body.index(self) + 1
        if not self.parent.parent:
            return 'k%d' % index
        return '%s-k%d' % (self.parent.parent.id, index)

    def __str__(self):
        if self.type == self.TRY:
            return 'TRY'
        if self.type == self.EXCEPT:
            return 'EXCEPT    %s' % self.pattern
        return 'ELSE'

    def visit(self, visitor):
        visitor.visit_try_branch(self)


@Body.register
class Return(BodyItem):
    type = BodyItem.RETURN
    repr_args = ('values',)
    __slots__ = ['values']

    def __init__(self, values=(), parent=None):
        self.values = values
        self.parent = parent

    def visit(self, visitor):
        visitor.visit_return(self)
