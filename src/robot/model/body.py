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

import re
from typing import (Any, Callable, cast, Generic, Iterable, Type, TYPE_CHECKING,
                    TypeVar, Union)

from robot.utils import copy_signature, KnownAtRuntime

from .itemlist import ItemList
from .modelobject import DataDict, full_name, ModelObject

if TYPE_CHECKING:
    from robot.result.model import ForIteration, WhileIteration
    from robot.running.model import UserKeyword, ResourceFile
    from .control import (Break, Continue, Error, For, If, IfBranch, Return,
                          Try, TryBranch, While)
    from .keyword import Keyword
    from .message import Message
    from .testcase import TestCase
    from .testsuite import TestSuite


BodyItemParent = Union['TestSuite', 'TestCase', 'UserKeyword', 'For', 'ForIteration',
                       'If', 'IfBranch', 'Try', 'TryBranch', 'While', 'WhileIteration',
                       'Keyword', 'Return', 'Continue', 'Break', 'Error', None]
BI = TypeVar('BI', bound='BodyItem')
KW = TypeVar('KW', bound='Keyword')
F = TypeVar('F', bound='For')
W = TypeVar('W', bound='While')
I = TypeVar('I', bound='If')
T = TypeVar('T', bound='Try')
R = TypeVar('R', bound='Return')
C = TypeVar('C', bound='Continue')
B = TypeVar('B', bound='Break')
M = TypeVar('M', bound='Message')
E = TypeVar('E', bound='Error')
IT = TypeVar('IT', bound='IfBranch|TryBranch')


class BodyItem(ModelObject):
    KEYWORD = 'KEYWORD'
    SETUP = 'SETUP'
    TEARDOWN = 'TEARDOWN'
    FOR = 'FOR'
    ITERATION = 'ITERATION'
    IF_ELSE_ROOT = 'IF/ELSE ROOT'
    IF = 'IF'
    ELSE_IF = 'ELSE IF'
    ELSE = 'ELSE'
    TRY_EXCEPT_ROOT = 'TRY/EXCEPT ROOT'
    TRY = 'TRY'
    EXCEPT = 'EXCEPT'
    FINALLY = 'FINALLY'
    WHILE = 'WHILE'
    RETURN = 'RETURN'
    CONTINUE = 'CONTINUE'
    BREAK = 'BREAK'
    ERROR = 'ERROR'
    MESSAGE = 'MESSAGE'
    type = None
    __slots__ = ['parent']

    @property
    def id(self) -> 'str|None':
        """Item id in format like ``s1-t3-k1``.

        See :attr:`TestSuite.id <robot.model.testsuite.TestSuite.id>` for
        more information.

        ``id`` is ``None`` only in these special cases:

        - Keyword uses a placeholder for ``setup`` or ``teardown`` when
          a ``setup`` or ``teardown`` is not actually used.
        - With :class:`~robot.model.control.If` and :class:`~robot.model.control.Try`
          instances representing IF/TRY structure roots.
        """
        return self._get_id(self.parent)

    def _get_id(self, parent: 'BodyItemParent|ResourceFile') -> str:
        if not parent:
            return 'k1'
        # This algorithm must match the id creation algorithm in the JavaScript side
        # or linking to warnings and errors won't work.
        steps = []
        if getattr(parent, 'has_setup', False):
            steps.append(parent.setup)          # type: ignore - Use Protocol with RF 7.
        if hasattr(parent, 'body'):
            steps.extend(step for step in
                         parent.body.flatten()  # type: ignore - Use Protocol with RF 7.
                         if step.type != self.MESSAGE)
        if getattr(parent, 'has_teardown', False):
            steps.append(parent.teardown)       # type: ignore - Use Protocol with RF 7.
        index = steps.index(self) if self in steps else len(steps)
        parent_id = getattr(parent, 'id', None)
        return f'{parent_id}-k{index + 1}' if parent_id else f'k{index + 1}'

    def to_dict(self) -> DataDict:
        raise NotImplementedError


class BaseBody(ItemList[BodyItem], Generic[KW, F, W, I, T, R, C, B, M, E]):
    """Base class for Body and Branches objects."""
    __slots__ = []
    # Set using 'BaseBody.register' when these classes are created.
    keyword_class: Type[KW] = KnownAtRuntime
    for_class: Type[F] = KnownAtRuntime
    while_class: Type[W] = KnownAtRuntime
    if_class: Type[I] = KnownAtRuntime
    try_class: Type[T] = KnownAtRuntime
    return_class: Type[R] = KnownAtRuntime
    continue_class: Type[C] = KnownAtRuntime
    break_class: Type[B] = KnownAtRuntime
    message_class: Type[M] = KnownAtRuntime
    error_class: Type[E] = KnownAtRuntime

    def __init__(self, parent: BodyItemParent = None,
                 items: 'Iterable[BodyItem|DataDict]' = ()):
        super().__init__(BodyItem, {'parent': parent}, items)

    def _item_from_dict(self, data: DataDict) -> BodyItem:
        item_type = data.get('type', None)
        if not item_type:
            item_class = self.keyword_class
        elif item_type == BodyItem.IF_ELSE_ROOT:
            item_class = self.if_class
        elif item_type == BodyItem.TRY_EXCEPT_ROOT:
            item_class = self.try_class
        else:
            item_class = getattr(self, item_type.lower() + '_class')
        item_class = cast(Type[BodyItem], item_class)
        return item_class.from_dict(data)

    @classmethod
    def register(cls, item_class: Type[BI]) -> Type[BI]:
        name_parts = re.findall('([A-Z][a-z]+)', item_class.__name__) + ['class']
        name = '_'.join(name_parts).lower()
        if not hasattr(cls, name):
            raise TypeError(f"Cannot register '{name}'.")
        setattr(cls, name, item_class)
        return item_class

    @property
    def create(self):
        raise AttributeError(
            f"'{full_name(self)}' object has no attribute 'create'. "
            f"Use item specific methods like 'create_keyword' instead."
        )

    def _create(self, cls: 'Type[BI]', name: str, args: 'tuple[Any]',
                kwargs: 'dict[str, Any]') -> BI:
        if cls is KnownAtRuntime:
            raise TypeError(f"'{full_name(self)}' object does not support '{name}'.")
        return self.append(cls(*args, **kwargs))  # type: ignore

    @copy_signature(keyword_class)
    def create_keyword(self, *args, **kwargs) -> keyword_class:
        return self._create(self.keyword_class, 'create_keyword', args, kwargs)

    @copy_signature(for_class)
    def create_for(self, *args, **kwargs) -> for_class:
        return self._create(self.for_class, 'create_for', args, kwargs)

    @copy_signature(if_class)
    def create_if(self, *args, **kwargs) -> if_class:
        return self._create(self.if_class, 'create_if', args, kwargs)

    @copy_signature(try_class)
    def create_try(self, *args, **kwargs) -> try_class:
        return self._create(self.try_class, 'create_try', args, kwargs)

    @copy_signature(while_class)
    def create_while(self, *args, **kwargs) -> while_class:
        return self._create(self.while_class, 'create_while', args, kwargs)

    @copy_signature(return_class)
    def create_return(self, *args, **kwargs) -> return_class:
        return self._create(self.return_class, 'create_return', args, kwargs)

    @copy_signature(continue_class)
    def create_continue(self, *args, **kwargs) -> continue_class:
        return self._create(self.continue_class, 'create_continue', args, kwargs)

    @copy_signature(break_class)
    def create_break(self, *args, **kwargs) -> break_class:
        return self._create(self.break_class, 'create_break', args, kwargs)

    @copy_signature(message_class)
    def create_message(self, *args, **kwargs) -> message_class:
        return self._create(self.message_class, 'create_message', args, kwargs)

    @copy_signature(error_class)
    def create_error(self, *args, **kwargs) -> error_class:
        return self._create(self.error_class, 'create_error', args, kwargs)

    def filter(self, keywords: 'bool|None' = None, messages: 'bool|None' = None,
               predicate: 'Callable[[T], bool]|None' = None):
        """Filter body items based on type and/or custom predicate.

        To include or exclude items based on types, give matching arguments
        ``True`` or ``False`` values. For example, to include only keywords,
        use ``body.filter(keywords=True)`` and to exclude messages use
        ``body.filter(messages=False)``. Including and excluding by types
        at the same time is not supported and filtering my ``messages``
        is supported only if the ``Body`` object actually supports messages.

        Custom ``predicate`` is a callable getting each body item as an argument
        that must return ``True/False`` depending on should the item be included
        or not.

        Selected items are returned as a list and the original body is not modified.

        It was earlier possible to filter also based on FOR and IF types.
        That support was removed in RF 5.0 because it was not considered useful
        in general and because adding support for all new control structures
        would have required extra work. To exclude all control structures, use
        ``body.filter(keywords=True, messages=True)`` and to only include them
        use ``body.filter(keywords=False``, messages=False)``. For more detailed
        filtering it is possible to use ``predicate``.
        """
        if messages is not None and self.message_class is KnownAtRuntime:
            raise TypeError(f"'{full_name(self)}' object does not support "
                            f"filtering by 'messages'.")
        return self._filter([(self.keyword_class, keywords),
                             (self.message_class, messages)], predicate)

    def _filter(self, types, predicate):
        include = tuple(cls for cls, activated in types if activated is True and cls)
        exclude = tuple(cls for cls, activated in types if activated is False and cls)
        if include and exclude:
            raise ValueError('Items cannot be both included and excluded by type.')
        items = list(self)
        if include:
            items = [item for item in items if isinstance(item, include)]
        if exclude:
            items = [item for item in items if not isinstance(item, exclude)]
        if predicate:
            items = [item for item in items if predicate(item)]
        return items

    def flatten(self) -> 'list[BodyItem]':
        """Return steps so that IF and TRY structures are flattened.

        Basically the IF/ELSE and TRY/EXCEPT root elements are replaced
        with their branches. This is how they are shown in log files.
        """
        roots = BodyItem.IF_ELSE_ROOT, BodyItem.TRY_EXCEPT_ROOT
        steps = []
        for item in self:
            if item.type in roots:
                item = cast('Try|If', item)
                steps.extend(item.body)
            else:
                steps.append(item)
        return steps


class Body(BaseBody['Keyword', 'For', 'While', 'If', 'Try', 'Return', 'Continue',
                    'Break', 'Message', 'Error']):
    """A list-like object representing a body of a test, keyword, etc.

    Body contains the keywords and other structures such as FOR loops.
    """
    pass


class BranchType(Generic[IT]):
    """Class that wrapps `Generic` as python doesn't allow multple generic inheritance"""
    pass


class BaseBranches(BaseBody[KW, F, W, I, T, R, C, B, M, E], BranchType[IT]):
    """A list-like object representing IF and TRY branches."""
    __slots__ = ['branch_class']
    branch_type: Type[IT] = KnownAtRuntime

    def __init__(self, branch_class: Type[IT],
                 parent: BodyItemParent = None,
                 items: 'Iterable[BodyItem|DataDict]' = ()):
        self.branch_class = branch_class
        super().__init__(parent, items)

    def _item_from_dict(self, data: DataDict) -> IT:
        return self.branch_class.from_dict(data)

    @copy_signature(branch_type)
    def create_branch(self, *args, **kwargs) -> IT:
        return self._create(self.branch_class, 'create_branch', args, kwargs)
