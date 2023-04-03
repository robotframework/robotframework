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
    """Represents ``FOR`` loops.

    :attr:`flavor` specifies the flavor, and it can be ``IN``, ``IN RANGE``,
    ``IN ENUMERATE`` or ``IN ZIP``.
    """
    type = BodyItem.FOR
    body_class = Body
    repr_args = ('variables', 'flavor', 'values', 'start', 'mode', 'fill')
    __slots__ = ['variables', 'flavor', 'values', 'start', 'mode', 'fill']

    def __init__(self, variables=(), flavor='IN', values=(), start=None, mode=None,
                 fill=None, parent=None):
        self.variables = variables
        self.flavor = flavor
        self.values = values
        self.start = start
        self.mode = mode
        self.fill = fill
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
        parts = ['FOR', *self.variables, self.flavor, *self.values]
        for name, value in [('start', self.start),
                            ('mode', self.mode),
                            ('fill', self.fill)]:
            if value is not None:
                parts.append(f'{name}={value}')
        return '    '.join(parts)

    def _include_in_repr(self, name, value):
        return name not in ('start', 'mode', 'fill') or value is not None

    def to_dict(self):
        data = {'type': self.type,
                'variables': list(self.variables),
                'flavor': self.flavor,
                'values': list(self.values),
                'body': self.body.to_dicts()}
        for name, value in [('start', self.start),
                            ('mode', self.mode),
                            ('fill', self.fill)]:
            if value is not None:
                data[name] = value
        return data


@Body.register
class While(BodyItem):
    """Represents ``WHILE`` loops."""
    type = BodyItem.WHILE
    body_class = Body
    repr_args = ('condition', 'limit', 'on_limit', 'on_limit_message')
    __slots__ = ['condition', 'limit', 'on_limit', 'on_limit_message']

    def __init__(self, condition=None, limit=None, on_limit=None,
                 on_limit_message=None, parent=None):
        self.condition = condition
        self.on_limit = on_limit
        self.limit = limit
        self.on_limit_message = on_limit_message
        self.parent = parent
        self.body = None

    @setter
    def body(self, body):
        return self.body_class(self, body)

    def visit(self, visitor):
        visitor.visit_while(self)

    def __str__(self):
        parts = ['WHILE']
        if self.condition is not None:
            parts.append(self.condition)
        if self.limit is not None:
            parts.append(f'limit={self.limit}')
        if self.on_limit is not None:
            parts.append(f'limit={self.on_limit}')
        if self.on_limit_message is not None:
            parts.append(f'on_limit_message={self.on_limit_message}')
        return '    '.join(parts)

    def _include_in_repr(self, name, value):
        return name == 'condition' or value is not None

    def to_dict(self):
        data = {'type': self.type}
        if self.condition:
            data['condition'] = self.condition
        if self.limit:
            data['limit'] = self.limit
        if self.on_limit_message:
            data['on_limit_message'] = self.on_limit_message
        data['body'] = self.body.to_dicts()
        return data


class IfBranch(BodyItem):
    """Represents individual ``IF``, ``ELSE IF`` or ``ELSE`` branch."""
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
            return self._get_id(self.parent)
        return self._get_id(self.parent.parent)

    def __str__(self):
        if self.type == self.IF:
            return 'IF    %s' % self.condition
        if self.type == self.ELSE_IF:
            return 'ELSE IF    %s' % self.condition
        return 'ELSE'

    def visit(self, visitor):
        visitor.visit_if_branch(self)

    def to_dict(self):
        data = {'type': self.type,
                'condition': self.condition,
                'body': self.body.to_dicts()}
        if self.type == self.ELSE:
            data.pop('condition')
        return data


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

    def to_dict(self):
        return {'type': self.type, 'body': self.body.to_dicts()}


class TryBranch(BodyItem):
    """Represents individual ``TRY``, ``EXCEPT``, ``ELSE`` or ``FINALLY`` branch."""
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
            return self._get_id(self.parent)
        return self._get_id(self.parent.parent)

    def __str__(self):
        if self.type != BodyItem.EXCEPT:
            return self.type
        parts = ['EXCEPT', *self.patterns]
        if self.pattern_type:
            parts.append(f'type={self.pattern_type}')
        if self.variable:
            parts.extend(['AS', self.variable])
        return '    '.join(parts)

    def _include_in_repr(self, name, value):
        return name == 'type' or value

    def visit(self, visitor):
        visitor.visit_try_branch(self)

    def to_dict(self):
        data = {'type': self.type}
        if self.type == self.EXCEPT:
            data['patterns'] = list(self.patterns)
            if self.pattern_type:
                data['pattern_type'] = self.pattern_type
            if self.variable:
                data['variable'] = self.variable
        data['body'] = self.body.to_dicts()
        return data


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

    def to_dict(self):
        return {'type': self.type, 'body': self.body.to_dicts()}


@Body.register
class Return(BodyItem):
    """Represents ``RETURN``."""
    type = BodyItem.RETURN
    repr_args = ('values',)
    __slots__ = ['values']

    def __init__(self, values=(), parent=None):
        self.values = values
        self.parent = parent

    def visit(self, visitor):
        visitor.visit_return(self)

    def to_dict(self):
        return {'type': self.type, 'values': list(self.values)}


@Body.register
class Continue(BodyItem):
    """Represents ``CONTINUE``."""
    type = BodyItem.CONTINUE
    __slots__ = []

    def __init__(self, parent=None):
        self.parent = parent

    def visit(self, visitor):
        visitor.visit_continue(self)

    def to_dict(self):
        return {'type': self.type}


@Body.register
class Break(BodyItem):
    """Represents ``BREAK``."""
    type = BodyItem.BREAK
    __slots__ = []

    def __init__(self, parent=None):
        self.parent = parent

    def visit(self, visitor):
        visitor.visit_break(self)

    def to_dict(self):
        return {'type': self.type}


@Body.register
class Error(BodyItem):
    """Represents syntax error in data.

    For example, an invalid setting like ``[Setpu]`` or ``END`` in wrong place.
    """
    type = BodyItem.ERROR
    __slots__ = ['values']

    def __init__(self, values=(), parent=None):
        self.values = values
        self.parent = parent

    def visit(self, visitor):
        visitor.visit_error(self)

    def to_dict(self):
        return {'type': self.type, 'values': list(self.values)}
