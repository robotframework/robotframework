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
    __slots__ = []
    KEYWORD_TYPE  = 'kw'
    SETUP_TYPE    = 'setup'
    TEARDOWN_TYPE = 'teardown'
    FOR_TYPE      = 'for'
    FOR_ITEM_TYPE = 'foritem'
    IF_TYPE       = 'if'
    ELSE_IF_TYPE  = 'elseif'
    ELSE_TYPE     = 'else'


class Body(ItemList):
    """A list-like object representing body of a suite, a test or a keyword.

    Body contains the keywords and other structures such as for loops.
    """
    __slots__ = []
    # Set using 'Body.register' when these classes are created.
    keyword_class = None
    for_class = None
    if_class = None

    def __init__(self, parent=None, body=None):
        ItemList.__init__(self, BodyItem, {'parent': parent}, body)

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

    def __setitem__(self, index, item):
        old = self[index]
        ItemList.__setitem__(self, index, item)
        self[index]._sort_key = old._sort_key
