#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

from robot import utils

from itemlist import ItemList
from message import Message
from modelobject import ModelObject


class Keyword(ModelObject):
    __slots__ = ['parent', 'name', 'doc', 'args', 'type', 'timeout']
    message_class = Message
    KEYWORD_TYPE = 'kw'
    SETUP_TYPE = 'setup'
    TEARDOWN_TYPE = 'teardown'
    FOR_LOOP_TYPE = 'for'
    FOR_ITEM_TYPE = 'foritem'

    def __init__(self, name='', doc='', args=None, type='kw', timeout=''):
        self.parent = None
        self.name = name
        self.doc = doc
        self.args = args or []
        self.type = type
        self.timeout = timeout
        self.messages = []
        self.keywords = []

    @utils.setter
    def keywords(self, keywords):
        return Keywords(self.__class__, keywords, parent=self)

    @utils.setter
    def messages(self, messages):
        return ItemList(self.message_class, messages, parent=self)

    @property
    def id(self):
        if not self.parent:
            return 'k1'
        return '%s-k%d' % (self.parent.id, self.parent.keywords.index(self)+1)

    def visit(self, visitor):
        visitor.visit_keyword(self)


class Keywords(ItemList):
    __slots__ = []

    def __init__(self, keyword_class=Keyword, items=None, parent=None):
        ItemList.__init__(self, keyword_class, items, parent=parent)

    @property
    def setup(self):
        return self[0] if (self and self[0].type == 'setup') else None

    @property
    def teardown(self):
        return self[-1] if (self and self[-1].type == 'teardown') else None

    @property
    def all(self):
        return self

    @property
    def normal(self):
        for kw in self:
            if kw.type in ('kw', 'for', 'foritem'):
                yield kw
