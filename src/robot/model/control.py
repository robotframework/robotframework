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

import sys
from typing import Any, cast, Sequence, TypeVar, TYPE_CHECKING
if sys.version_info >= (3, 8):
    from typing import Literal

from robot.utils import setter

from .body import Body, BodyItem, BodyItemParent, BaseBranches
from .keyword import Keywords
from .modelobject import DataDict
from .visitor import SuiteVisitor

if TYPE_CHECKING:
    from robot.model import Keyword, Message

IT = TypeVar('IT', bound='IfBranch|TryBranch')


class Branches(BaseBranches['Keyword', 'For', 'While', 'If', 'Try', 'Return', 'Continue',
                            'Break', 'Message', 'Error', IT]):
    pass


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

    def __init__(self, variables: Sequence[str] = (),
                 flavor: "Literal['IN', 'IN RANGE', 'IN ENUMERATE', 'IN ZIP']" = 'IN',
                 values: Sequence[str] = (),
                 start: 'str|None' = None,
                 mode: 'str|None' = None,
                 fill: 'str|None' = None,
                 parent: BodyItemParent = None):
        self.variables = tuple(variables)
        self.flavor = flavor
        self.values = tuple(values)
        self.start = start
        self.mode = mode
        self.fill = fill
        self.parent = parent
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        return self.body_class(self, body)

    @property
    def keywords(self):
        """Deprecated since Robot Framework 4.0. Use :attr:`body` instead."""
        return Keywords(self, self.body)

    @keywords.setter
    def keywords(self, keywords):
        Keywords.raise_deprecation_error()

    def visit(self, visitor: SuiteVisitor):
        visitor.visit_for(self)

    def __str__(self):
        parts = ['FOR', *self.variables, self.flavor, *self.values]
        for name, value in [('start', self.start),
                            ('mode', self.mode),
                            ('fill', self.fill)]:
            if value is not None:
                parts.append(f'{name}={value}')
        return '    '.join(parts)

    def _include_in_repr(self, name: str, value: Any) -> bool:
        return name not in ('start', 'mode', 'fill') or value is not None

    def to_dict(self) -> DataDict:
        data = {'type': self.type,
                'variables': self.variables,
                'flavor': self.flavor,
                'values': self.values}
        for name, value in [('start', self.start),
                            ('mode', self.mode),
                            ('fill', self.fill)]:
            if value is not None:
                data[name] = value
        data['body'] = self.body.to_dicts()
        return data


@Body.register
class While(BodyItem):
    """Represents ``WHILE`` loops."""
    type = BodyItem.WHILE
    body_class = Body
    repr_args = ('condition', 'limit', 'on_limit', 'on_limit_message')
    __slots__ = ['condition', 'limit', 'on_limit', 'on_limit_message']

    def __init__(self, condition: 'str|None' = None,
                 limit: 'str|None' = None,
                 on_limit: 'str|None' = None,
                 on_limit_message: 'str|None' = None,
                 parent: BodyItemParent = None):
        self.condition = condition
        self.on_limit = on_limit
        self.limit = limit
        self.on_limit_message = on_limit_message
        self.parent = parent
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        return self.body_class(self, body)

    def visit(self, visitor: SuiteVisitor):
        visitor.visit_while(self)

    def __str__(self) -> str:
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

    def _include_in_repr(self, name: str, value: Any) -> bool:
        return name == 'condition' or value is not None

    def to_dict(self) -> DataDict:
        data: DataDict = {'type': self.type}
        for name, value in [('condition', self.condition),
                            ('limit', self.limit),
                            ('on_limit', self.on_limit),
                            ('on_limit_message', self.on_limit_message)]:
            if value is not None:
                data[name] = value
        data['body'] = self.body.to_dicts()
        return data


class IfBranch(BodyItem):
    """Represents individual ``IF``, ``ELSE IF`` or ``ELSE`` branch."""
    body_class = Body
    repr_args = ('type', 'condition')
    __slots__ = ['type', 'condition']

    def __init__(self, type: str = BodyItem.IF,
                 condition: 'str|None' = None,
                 parent: BodyItemParent = None):
        self.type = type
        self.condition = condition
        self.parent = parent
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        return self.body_class(self, body)

    @property
    def id(self) -> str:
        """Branch id omits IF/ELSE root from the parent id part."""
        if not self.parent:
            return 'k1'
        if not self.parent.parent:
            return self._get_id(self.parent)
        return self._get_id(self.parent.parent)

    def __str__(self) -> str:
        if self.type == self.IF:
            return f'IF    {self.condition}'
        if self.type == self.ELSE_IF:
            return f'ELSE IF    {self.condition}'
        return 'ELSE'

    def visit(self, visitor: SuiteVisitor):
        visitor.visit_if_branch(self)

    def to_dict(self) -> DataDict:
        data = {'type': self.type}
        if self.condition:
            data['condition'] = self.condition
        data['body'] = self.body.to_dicts()
        return data


@Body.register
class If(BodyItem):
    """IF/ELSE structure root. Branches are stored in :attr:`body`."""
    type = BodyItem.IF_ELSE_ROOT
    branch_class = IfBranch
    branches_class = Branches[branch_class]
    __slots__ = []

    def __init__(self, parent: BodyItemParent = None):
        self.parent = parent
        self.body = ()

    @setter
    def body(self, branches: 'Sequence[BodyItem|DataDict]') -> branches_class:
        return self.branches_class(self.branch_class, self, branches)

    @property
    def id(self) -> None:
        """Root IF/ELSE id is always ``None``."""
        return None

    def visit(self, visitor: SuiteVisitor):
        visitor.visit_if(self)

    def to_dict(self) -> DataDict:
        return {'type': self.type,
                'body': self.body.to_dicts()}


class TryBranch(BodyItem):
    """Represents individual ``TRY``, ``EXCEPT``, ``ELSE`` or ``FINALLY`` branch."""
    body_class = Body
    repr_args = ('type', 'patterns', 'pattern_type', 'variable')
    __slots__ = ['type', 'patterns', 'pattern_type', 'variable']

    def __init__(self, type: str = BodyItem.TRY,
                 patterns: Sequence[str] = (),
                 pattern_type: 'str|None' = None,
                 variable: 'str|None' = None,
                 parent: BodyItemParent = None):
        if (patterns or pattern_type or variable) and type != BodyItem.EXCEPT:
            raise TypeError(f"'{type}' branches do not accept patterns or variables.")
        self.type = type
        self.patterns = tuple(patterns)
        self.pattern_type = pattern_type
        self.variable = variable
        self.parent = parent
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        return self.body_class(self, body)

    @property
    def id(self) -> str:
        """Branch id omits TRY/EXCEPT root from the parent id part."""
        if not self.parent:
            return 'k1'
        if not self.parent.parent:
            return self._get_id(self.parent)
        return self._get_id(self.parent.parent)

    def __str__(self) -> str:
        if self.type != BodyItem.EXCEPT:
            return self.type
        parts = ['EXCEPT', *self.patterns]
        if self.pattern_type:
            parts.append(f'type={self.pattern_type}')
        if self.variable:
            parts.extend(['AS', self.variable])
        return '    '.join(parts)

    def _include_in_repr(self, name: str, value: Any) -> bool:
        return bool(value)

    def visit(self, visitor: SuiteVisitor):
        visitor.visit_try_branch(self)

    def to_dict(self) -> DataDict:
        data: DataDict = {'type': self.type}
        if self.type == self.EXCEPT:
            data['patterns'] = self.patterns
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
    branches_class = Branches[branch_class]
    __slots__ = []

    def __init__(self, parent: BodyItemParent = None):
        self.parent = parent
        self.body = ()

    @setter
    def body(self, branches: 'Sequence[TryBranch|DataDict]') -> branches_class:
        return self.branches_class(self.branch_class, self, branches)

    @property
    def try_branch(self) -> TryBranch:
        if self.body and self.body[0].type == BodyItem.TRY:
            return cast(TryBranch, self.body[0])
        raise TypeError("No 'TRY' branch or 'TRY' branch is not first.")

    @property
    def except_branches(self) -> 'list[TryBranch]':
        return [cast(TryBranch, branch) for branch in self.body
                if branch.type == BodyItem.EXCEPT]

    @property
    def else_branch(self) -> 'TryBranch|None':
        for branch in self.body:
            if branch.type == BodyItem.ELSE:
                return cast(TryBranch, branch)
        return None

    @property
    def finally_branch(self):
        if self.body and self.body[-1].type == BodyItem.FINALLY:
            return cast(TryBranch, self.body[-1])
        return None

    @property
    def id(self) -> None:
        """Root TRY/EXCEPT id is always ``None``."""
        return None

    def visit(self, visitor: SuiteVisitor):
        visitor.visit_try(self)

    def to_dict(self) -> DataDict:
        return {'type': self.type,
                'body': self.body.to_dicts()}


@Body.register
class Return(BodyItem):
    """Represents ``RETURN``."""
    type = BodyItem.RETURN
    repr_args = ('values',)
    __slots__ = ['values']

    def __init__(self, values: Sequence[str] = (),
                 parent: BodyItemParent = None):
        self.values = tuple(values)
        self.parent = parent

    def visit(self, visitor: SuiteVisitor):
        visitor.visit_return(self)

    def to_dict(self) -> DataDict:
        return {'type': self.type,
                'values': self.values}


@Body.register
class Continue(BodyItem):
    """Represents ``CONTINUE``."""
    type = BodyItem.CONTINUE
    __slots__ = []

    def __init__(self, parent: BodyItemParent = None):
        self.parent = parent

    def visit(self, visitor: SuiteVisitor):
        visitor.visit_continue(self)

    def to_dict(self) -> DataDict:
        return {'type': self.type}


@Body.register
class Break(BodyItem):
    """Represents ``BREAK``."""
    type = BodyItem.BREAK
    __slots__ = []

    def __init__(self, parent: BodyItemParent = None):
        self.parent = parent

    def visit(self, visitor: SuiteVisitor):
        visitor.visit_break(self)

    def to_dict(self) -> DataDict:
        return {'type': self.type}


@Body.register
class Error(BodyItem):
    """Represents syntax error in data.

    For example, an invalid setting like ``[Setpu]`` or ``END`` in wrong place.
    """
    type = BodyItem.ERROR
    repr_args = ('values',)
    __slots__ = ['values']

    def __init__(self, values: Sequence[str] = (),
                 parent: BodyItemParent = None):
        self.values = tuple(values)
        self.parent = parent

    def visit(self, visitor: SuiteVisitor):
        visitor.visit_error(self)

    def to_dict(self) -> DataDict:
        return {'type': self.type,
                'values': self.values}
