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

from typing import cast, Sequence, Type, TYPE_CHECKING
import warnings

from .body import Body, BodyItem, BodyItemParent
from .itemlist import ItemList
from .modelobject import DataDict

if TYPE_CHECKING:
    from .visitor import SuiteVisitor


@Body.register
class Keyword(BodyItem):
    """Base model for a single keyword.

    Extended by :class:`robot.running.model.Keyword` and
    :class:`robot.result.model.Keyword`.
    """
    repr_args = ('name', 'args', 'assign')
    __slots__ = ['_name', 'args', 'assign', 'type']

    def __init__(self, name: 'str|None' = '',
                 args: Sequence[str] = (),
                 assign: Sequence[str] = (),
                 type: str = BodyItem.KEYWORD,
                 parent: BodyItemParent = None):
        self.name = name
        self.args = tuple(args)
        self.assign = tuple(assign)
        self.type = type
        self.parent = parent

    @property
    def name(self) -> 'str|None':
        return self._name

    @name.setter
    def name(self, name: 'str|None'):
        self._name = name

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


# FIXME: Remote in RF 7.
class Keywords(ItemList[BodyItem]):
    """A list-like object representing keywords in a suite, a test or a keyword.

    Read-only and deprecated since Robot Framework 4.0.
    """
    __slots__ = []
    deprecation_message = (
        "'keywords' attribute is read-only and deprecated since Robot Framework 4.0. "
        "Use 'body', 'setup' or 'teardown' instead."
    )

    def __init__(self, parent: BodyItemParent = None,
                 keywords: Sequence[BodyItem] = ()):
        warnings.warn(self.deprecation_message, UserWarning)
        ItemList.__init__(self, object, {'parent': parent})
        if keywords:
            ItemList.extend(self, keywords)

    @property
    def setup(self) -> 'Keyword|None':
        if self and self[0].type == 'SETUP':
            return cast(Keyword, self[0])
        return None

    @setup.setter
    def setup(self, kw):
        self.raise_deprecation_error()

    def create_setup(self, *args, **kwargs):
        self.raise_deprecation_error()

    @property
    def teardown(self) -> 'Keyword|None':
        if self and self[-1].type == 'TEARDOWN':
            return cast(Keyword, self[-1])
        return None

    @teardown.setter
    def teardown(self, kw: Keyword):
        self.raise_deprecation_error()

    def create_teardown(self, *args, **kwargs):
        self.raise_deprecation_error()

    @property
    def all(self) -> 'Keywords':
        """Iterates over all keywords, including setup and teardown."""
        return self

    @property
    def normal(self) -> 'list[BodyItem]':
        """Iterates over normal keywords, omitting setup and teardown."""
        return [kw for kw in self if kw.type not in ('SETUP', 'TEARDOWN')]

    def __setitem__(self, index: int, item: Keyword):
        self.raise_deprecation_error()

    def create(self, *args, **kwargs):
        self.raise_deprecation_error()

    def append(self, item: Keyword):
        self.raise_deprecation_error()

    def extend(self, items: Sequence[Keyword]):
        self.raise_deprecation_error()

    def insert(self, index: int, item: Keyword):
        self.raise_deprecation_error()

    def pop(self, *index: int):
        self.raise_deprecation_error()

    def remove(self, item: Keyword):
        self.raise_deprecation_error()

    def clear(self):
        self.raise_deprecation_error()

    def __delitem__(self, index: int):
        self.raise_deprecation_error()

    def sort(self):
        self.raise_deprecation_error()

    def reverse(self):
        self.raise_deprecation_error()

    @classmethod
    def raise_deprecation_error(cls: 'Type[Keywords]'):
        raise AttributeError(cls.deprecation_message)
