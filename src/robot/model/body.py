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
from typing import cast, Generic, Iterable, Mapping, Type, TypeVar, TYPE_CHECKING

from .itemlist import ItemList
from .modelobject import ModelObject, full_name

if TYPE_CHECKING:
    from .control import Break, Continue, Error, For, If, Return, Try, While
    from .keyword import Keyword
    from .message import Message
    from .testcase import TestCase
    from .testsuite import TestSuite

C = TypeVar('C', bound='BodyItem')
T = TypeVar('T', 'Try', 'If')


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
        """
        # This algorithm must match the id creation algorithm in the JavaScript side
        # or linking to warnings and errors won't work.
        if not self:
            return None
        if not self.parent:
            return 'k1'
        return self._get_id(self.parent)

    def _get_id(self, parent: 'TestSuite|TestCase|T') -> str:
        steps = []
        if getattr(parent, 'has_setup', False):
            parent = cast('TestSuite|TestCase', parent)
            steps.append(parent.setup)
        if hasattr(parent, 'body'):
            parent = cast('T', parent)
            steps.extend(step for step in parent.body.flatten()
                         if step.type != self.MESSAGE)
        if getattr(parent, 'has_teardown', False):
            parent = cast('TestSuite|TestCase', parent)
            steps.append(parent.teardown)
        index = steps.index(self) if self in steps else len(steps)
        parent_id = parent.id
        return f'{parent_id}-k{index + 1}' if parent_id else f'k{index + 1}'

    def to_dict(self):
        raise NotImplementedError


class BaseBody(ItemList[BodyItem]):
    """Base class for Body and Branches objects."""
    __slots__ = []
    # Set using 'BaseBody.register' when these classes are created.
    keyword_class = None
    for_class = None
    while_class = None
    if_class = None
    try_class = None
    return_class = None
    continue_class = None
    break_class = None
    message_class = None
    error_class = None

    def __init__(self, parent: 'TestSuite|TestCase|BodyItem|None' = None,
                 items: 'Iterable[C|Mapping]' = ()):
        super().__init__(BodyItem, {'parent': parent}, items)

    def _item_from_dict(self, data: Mapping) -> BodyItem:
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
    def register(cls: 'Type[BaseBody]', item_class: Type[C]) -> Type[C]:
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

    def create_keyword(self, *args, **kwargs) -> 'Keyword':
        return self._create(self.keyword_class, 'create_keyword', args, kwargs)

    def _create(self, cls: 'Type[C]|None', name: str, args, kwargs) -> C:
        if cls is None:
            raise TypeError(f"'{full_name(self)}' object does not support '{name}'.")
        return self.append(cls(*args, **kwargs))

    def create_for(self, *args, **kwargs) -> 'For':
        return self._create(self.for_class, 'create_for', args, kwargs)

    def create_if(self, *args, **kwargs) -> 'If':
        return self._create(self.if_class, 'create_if', args, kwargs)

    def create_try(self, *args, **kwargs) -> 'Try':
        return self._create(self.try_class, 'create_try', args, kwargs)

    def create_while(self, *args, **kwargs) -> 'While':
        return self._create(self.while_class, 'create_while', args, kwargs)

    def create_return(self, *args, **kwargs) -> 'Return':
        return self._create(self.return_class, 'create_return', args, kwargs)

    def create_continue(self, *args, **kwargs) -> 'Continue':
        return self._create(self.continue_class, 'create_continue', args, kwargs)

    def create_break(self, *args, **kwargs) -> 'Break':
        return self._create(self.break_class, 'create_break', args, kwargs)

    def create_message(self, *args, **kwargs) -> 'Message':
        return self._create(self.message_class, 'create_message', args, kwargs)

    def create_error(self, *args, **kwargs) -> 'Error':
        return self._create(self.error_class, 'create_error', args, kwargs)

    def filter(self, keywords=None, messages=None, predicate=None):
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
        if messages is not None and not self.message_class:
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

    def flatten(self) -> 'list[BodyItem|Try|If]':
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


class Body(BaseBody):
    """A list-like object representing a body of a test, keyword, etc.

    Body contains the keywords and other structures such as FOR loops.
    """
    pass


class Branches(BaseBody, Generic[T]):
    """A list-like object representing IF and TRY branches."""
    __slots__ = ['branch_class']

    def __init__(self, branch_class: Type[T],
                 parent: 'TestSuite|TestCase|BodyItem|None' = None,
                 items: 'Iterable[T|Mapping]' = ()):

        self.branch_class = branch_class
        super().__init__(parent, items)

    def _item_from_dict(self, data: Mapping) -> T:
        return self.branch_class.from_dict(data)

    def create_branch(self, *args, **kwargs):
        return self.append(self.branch_class(*args, **kwargs))
