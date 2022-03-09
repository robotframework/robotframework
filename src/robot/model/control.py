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

from .body import Body, BodyItem, Branches
from .keyword import Keywords


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
class While(BodyItem):
    type = BodyItem.WHILE
    body_class = Body
    repr_args = ('condition', 'limit')
    __slots__ = ['condition', 'limit']

    def __init__(self, condition=None, limit=None, parent=None):
        self.condition = condition
        self.limit = limit
        self.parent = parent
        self.body = None

    @setter
    def body(self, body):
        return self.body_class(self, body)

    def visit(self, visitor):
        visitor.visit_while(self)

    def __str__(self):
        return f'WHILE    {self.condition}' + (f'    {self.limit}' if self.limit else '')


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
        """Branch id omits IF/ELSE root from the parent id part."""
        if not self.parent:
            return 'k1'
        if not self.parent.parent:
            return 'k%d' % (self.parent.body.index(self) + 1)
        return self._get_id(self.parent.parent)

    def __str__(self):
        if self.type == self.IF:
            return 'IF    %s' % self.condition
        if self.type == self.ELSE_IF:
            return 'ELSE IF    %s' % self.condition
        return 'ELSE'

    def visit(self, visitor):
        visitor.visit_if_branch(self)


@Body.register
class If(BodyItem):
    """IF/ELSE structure root. Branches are stored in :attr:`body`."""
    type = BodyItem.IF_ELSE_ROOT
    branch_class = IfBranch
    branches_class = Branches
    __slots__ = ['parent']

    def __init__(self, parent=None):
        self.parent = parent
        self.body = None

    @setter
    def body(self, branches):
        return self.branches_class(self.branch_class, self, branches)

    @property
    def id(self):
        """Root IF/ELSE id is always ``None``."""
        return None

    def visit(self, visitor):
        visitor.visit_if(self)


class TryBranch(BodyItem):
    body_class = Body
    repr_args = ('type', 'patterns', 'pattern_type', 'variable')
    __slots__ = ['type', 'patterns', 'pattern_type', 'variable']

    def __init__(self, type=BodyItem.TRY, patterns=(), pattern_type=None,
                 variable=None, parent=None):
        if (patterns or pattern_type or variable) and type != BodyItem.EXCEPT:
            raise TypeError(f"'{type}' branches do not accept patterns or variables.")
        self.type = type
        self.patterns = patterns
        self.pattern_type = pattern_type
        self.variable = variable
        self.parent = parent
        self.body = None

    @setter
    def body(self, body):
        return self.body_class(self, body)

    @property
    def id(self):
        """Branch id omits TRY/EXCEPT root from the parent id part."""
        if not self.parent:
            return 'k1'
        if not self.parent.parent:
            return 'k%d' % (self.parent.body.index(self) + 1)
        return self._get_id(self.parent.parent)

    def __str__(self):
        if self.type != BodyItem.EXCEPT:
            return self.type
        parts = ['EXCEPT'] + list(self.patterns)
        if self.pattern_type:
            parts.append(f'type={self.pattern_type}')
        if self.variable:
            parts.extend(['AS', self.variable])
        return '    '.join(parts)

    def __repr__(self):
        repr_args = self.repr_args if self.type == BodyItem.EXCEPT else ['type']
        return self._repr(repr_args)

    def visit(self, visitor):
        visitor.visit_try_branch(self)


@Body.register
class Try(BodyItem):
    """TRY/EXCEPT structure root. Branches are stored in :attr:`body`."""
    type = BodyItem.TRY_EXCEPT_ROOT
    branch_class = TryBranch
    branches_class = Branches
    __slots__ = []

    def __init__(self, parent=None):
        self.parent = parent
        self.body = None

    @setter
    def body(self, branches):
        return self.branches_class(self.branch_class, self, branches)

    @property
    def try_branch(self):
        if self.body and self.body[0].type == BodyItem.TRY:
            return self.body[0]
        raise TypeError("No 'TRY' branch or 'TRY' branch is not first.")

    @property
    def except_branches(self):
        return [branch for branch in self.body if branch.type == BodyItem.EXCEPT]

    @property
    def else_branch(self):
        for branch in self.body:
            if branch.type == BodyItem.ELSE:
                return branch
        return None

    @property
    def finally_branch(self):
        if self.body and self.body[-1].type == BodyItem.FINALLY:
            return self.body[-1]
        return None

    @property
    def id(self):
        """Root TRY/EXCEPT id is always ``None``."""
        return None

    def visit(self, visitor):
        visitor.visit_try(self)


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


@Body.register
class Continue(BodyItem):
    type = BodyItem.CONTINUE
    __slots__ = []

    def __init__(self, parent=None):
        self.parent = parent

    def visit(self, visitor):
        visitor.visit_continue(self)


@Body.register
class Break(BodyItem):
    type = BodyItem.BREAK
    __slots__ = []

    def __init__(self, parent=None):
        self.parent = parent

    def visit(self, visitor):
        visitor.visit_break(self)
