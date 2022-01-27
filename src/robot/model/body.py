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

from .itemlist import ItemList
from .modelobject import ModelObject


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
    MESSAGE = 'MESSAGE'
    type = None
    __slots__ = ['parent']

    @property
    def id(self):
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
        setup = getattr(self.parent, 'setup', None)
        body = getattr(self.parent, 'body', ())
        teardown = getattr(self.parent, 'teardown', None)
        steps = [step for step in [setup] + list(body) + [teardown]
                 if step and step.type != step.MESSAGE]
        return '%s-k%d' % (self.parent.id, steps.index(self) + 1)


class BaseBody(ItemList):
    """Base class for Body and Branches objects."""
    __slots__ = []
    # Set using 'Body.register' when these classes are created.
    keyword_class = None
    for_class = None
    if_class = None
    try_class = None
    while_class = None
    return_class = None
    continue_class = None
    break_class = None
    message_class = None

    def __init__(self, parent=None, items=None):
        ItemList.__init__(self, BodyItem, {'parent': parent}, items)

    @classmethod
    def register(cls, item_class):
        name_parts = re.findall('([A-Z][a-z]+)', item_class.__name__) + ['class']
        name = '_'.join(name_parts).lower()
        if not hasattr(cls, name):
            raise TypeError("Cannot register '%s'." % name)
        setattr(cls, name, item_class)
        return item_class

    @property
    def create(self):
        raise AttributeError(
            "'%s' object has no attribute 'create'. "
            "Use item specific methods like 'create_keyword' instead."
            % type(self).__name__
        )

    def create_keyword(self, *args, **kwargs):
        return self._create(self.keyword_class, 'create_keyword', args, kwargs)

    def _create(self, cls, name, args, kwargs):
        if cls is None:
            raise TypeError("'%s' object does not support '%s'."
                            % (type(self).__name__, name))
        return self.append(cls(*args, **kwargs))

    def create_for(self, *args, **kwargs):
        return self._create(self.for_class, 'create_for', args, kwargs)

    def create_if(self, *args, **kwargs):
        return self._create(self.if_class, 'create_if', args, kwargs)

    def create_try(self, *args, **kwargs):
        return self._create(self.try_class, 'create_try', args, kwargs)

    def create_while(self, *args, **kwargs):
        return self._create(self.while_class, 'create_while', args, kwargs)

    def create_return(self, *args, **kwargs):
        return self._create(self.return_class, 'create_return', args, kwargs)

    def create_continue(self, *args, **kwargs):
        return self._create(self.continue_class, 'create_continue', args, kwargs)

    def create_break(self, *args, **kwargs):
        return self._create(self.break_class, 'create_break', args, kwargs)

    def create_message(self, *args, **kwargs):
        return self._create(self.message_class, 'create_message', args, kwargs)

    # FIXME: Add `whiles` and possibly also `returns`, `breaks` and `continues´.
    # Could also consider having something generic like `controls` or `syntax`
    # to include/exclude all control structures. Or perhaps we don't need that
    # support at all and including/excluding using `keywords` and `messages` is
    # enough.
    def filter(self, keywords=None, fors=None, ifs=None, trys=None, messages=None,
               predicate=None):
        """Filter body items based on type and/or custom predicate.

        To include or exclude items based on types, give matching arguments
        ``True`` or ``False`` values. For example, to include only keywords, use
        ``body.filter(keywords=True)`` and to exclude FOR and IF constructs use
        ``body.filter(fors=False, ifs=False)``. Including and excluding by types
        at the same time is not supported.

        Custom ``predicate`` is a callable getting each body item as an argument
        that must return ``True/False`` depending on should the item be included
        or not.

        Selected items are returned as a list and the original body is not modified.
        """
        return self._filter([(self.keyword_class, keywords),
                             (self.for_class, fors),
                             (self.if_class, ifs),
                             (self.try_class, trys),
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


class Body(BaseBody):
    """A list-like object representing body of a suite, a test or a keyword.

    Body contains the keywords and other structures such as FOR loops.
    """
    pass


class Branches(BaseBody):
    """A list-like object representing branches IF and TRY objects contain."""
    __slots__ = ['branch_class']

    def __init__(self, branch_class, parent=None, items=None):
        self.branch_class = branch_class
        super().__init__(parent, items)

    def create_branch(self, *args, **kwargs):
        return self.append(self.branch_class(*args, **kwargs))
