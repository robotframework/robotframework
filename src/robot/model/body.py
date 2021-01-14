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

from .itemlist import ItemList
from .modelobject import ModelObject


class BodyItem(ModelObject):
    KEYWORD_TYPE  = 'kw'
    SETUP_TYPE    = 'setup'
    TEARDOWN_TYPE = 'teardown'
    FOR_TYPE      = 'for'
    FOR_ITEM_TYPE = 'foritem'
    IF_TYPE       = 'if'
    ELSE_IF_TYPE  = 'elseif'
    ELSE_TYPE     = 'else'
    MESSAGE_TYPE  = 'message'
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
        keywords = [item for item in [setup] + list(body) + [teardown]
                    if item and item.type != item.MESSAGE_TYPE]
        return '%s-k%d' % (self.parent.id, keywords.index(self) + 1)


class Body(ItemList):
    """A list-like object representing body of a suite, a test or a keyword.

    Body contains the keywords and other structures such as for loops.
    """
    __slots__ = []
    # Set using 'Body.register' when these classes are created.
    keyword_class = None
    for_class = None
    if_class = None

    def __init__(self, parent=None, items=None):
        ItemList.__init__(self, BodyItem, {'parent': parent}, items)

    @classmethod
    def register(cls, body_class):
        name = '%s_class' % body_class.__name__.lower()
        setattr(cls, name, body_class)
        return body_class

    def create(self, *args, **kwargs):
        raise AttributeError(
            "'Body' object has no attribute 'create'. "
            "Use item specific methods like 'create_keyword' instead."
        )

    def create_keyword(self, *args, **kwargs):
        return self.append(self.keyword_class(*args, **kwargs))

    def create_for(self, *args, **kwargs):
        return self.append(self.for_class(*args, **kwargs))

    def create_if(self, *args, **kwargs):
        return self.append(self.if_class(*args, **kwargs))

    def filter(self, keywords=None, fors=None, ifs=None, predicate=None):
        """Filter body items based on type and/or custom predicate.

        To include or exclude items based on types, give matching arguments
        ``True`` or ``False`` values. For example, to include only keywords, use
        ``body.filter(keywords=True)`` and to exclude FOR and IF constructs use
        ``body.filter(fors=False, ifs=False)``. Including and excluding by types
        at the same time is not supported.

        Custom ``predicate`` is a calleble getting each body item as an argument
        that must return ``True/False`` depending on should the item be included
        or not.

        Selected items are returned as a list and the original body is not modified.
        """
        return self._filter([(self.keyword_class, keywords),
                             (self.for_class, fors),
                             (self.if_class, ifs)], predicate)

    def _filter(self, types, predicate):
        include = tuple(cls for cls, activated in types if activated is True)
        exclude = tuple(cls for cls, activated in types if activated is False)
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
