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

from typing import Any, Dict, List, Sequence, Tuple, TYPE_CHECKING, Union

from .body import Body, BodyItem, BodyItemParent
from .modelobject import DataDict

if TYPE_CHECKING:
    from .visitor import SuiteVisitor


Arguments = Union[Sequence[Union[Any, Tuple[Any], Tuple[str, Any]]],
                  Tuple[List[Any], Dict[str, Any]]]


@Body.register
class Keyword(BodyItem):
    """Base model for a single keyword.

    Extended by :class:`robot.running.model.Keyword` and
    :class:`robot.result.model.Keyword`.

    Arguments from normal data are always strings, but other types are possible in
    programmatic usage. See the docstrings of the extending classes for more details.
    """
    repr_args = ('name', 'args', 'assign')
    __slots__ = ['name', 'args', 'assign', 'type']

    def __init__(self, name: 'str|None' = '',
                 args: Arguments = (),
                 assign: Sequence[str] = (),
                 type: str = BodyItem.KEYWORD,
                 parent: BodyItemParent = None):
        self.name = name
        self.args = tuple(args)
        self.assign = tuple(assign)
        self.type = type
        self.parent = parent

    @property
    def id(self) -> 'str|None':
        if not self:
            return None
        return super().id

    def visit(self, visitor: 'SuiteVisitor'):
        """:mod:`Visitor interface <robot.model.visitor>` entry-point."""
        if self:
            visitor.visit_keyword(self)

    def __bool__(self) -> bool:
        return self.name is not None

    def __str__(self) -> str:
        parts = list(self.assign) + [self.name] + list(self.args)
        return '    '.join(str(p) for p in parts)

    def to_dict(self) -> DataDict:
        data: DataDict = {'name': self.name}
        if self.args:
            data['args'] = self.args
        if self.assign:
            data['assign'] = self.assign
        return data
