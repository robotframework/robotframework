#  Copyright 2008-2014 Nokia Solutions and Networks
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

from itertools import chain
from operator import attrgetter

from robot.utils import setter

from .itemlist import ItemList
from .message import Message, Messages
from .modelobject import ModelObject


class Keyword(ModelObject):
    """Base model for single keyword."""
    __slots__ = ['parent', 'name', 'doc', 'args', 'type', 'timeout',
                 '_sort_key', '_next_child_sort_key']
    KEYWORD_TYPE = 'kw'
    SETUP_TYPE = 'setup'
    TEARDOWN_TYPE = 'teardown'
    FOR_LOOP_TYPE = 'for'
    FOR_ITEM_TYPE = 'foritem'
    keyword_class = None
    message_class = Message

    def __init__(self, name='', doc='', args=(), type='kw', timeout=None):
        #: :class:`~.model.testsuite.TestSuite` or
        #: :class:`~.model.testcase.TestCase` or
        #: :class:`~.model.keyword.Keyword` that contains this keyword.
        self.parent = None
        #: Keyword name.
        self.name = name
        #: Keyword documentation.
        self.doc = doc
        #: Keyword arguments, a list of strings.
        self.args = args
        #: 'SETUP', 'TEARDOWN' or 'KW'.
        self.type = type
        #: Keyword timeout.
        self.timeout = timeout
        #: Keyword messages as :class:`~.model.message.Message` instances.
        self.messages = None
        #: Child keywords as :class:`~.model.keyword.Keyword` instances.
        self.keywords = None
        self._sort_key = -1
        self._next_child_sort_key = 0

    @setter
    def parent(self, parent):
        if parent and parent is not self.parent:
            self._sort_key = getattr(parent, '_child_sort_key', -1)
        return parent

    @property
    def _child_sort_key(self):
        self._next_child_sort_key += 1
        return self._next_child_sort_key

    @setter
    def keywords(self, keywords):
        return Keywords(self.keyword_class or self.__class__, self, keywords)

    @setter
    def messages(self, messages):
        return Messages(self.message_class, self, messages)

    @property
    def children(self):
        """Child keywords and messages in creation order."""
        # It would be cleaner to store keywords/messages in same `children`
        # list and turn `keywords` and `messages` to properties that pick items
        # from it. That would require bigger changes to the model, though.
        return sorted(chain(self.keywords, self.messages),
                      key=attrgetter('_sort_key'))

    @property
    def id(self):
        if not self.parent:
            return 'k1'
        return '%s-k%d' % (self.parent.id, self.parent.keywords.index(self)+1)

    def visit(self, visitor):
        visitor.visit_keyword(self)


class Keywords(ItemList):
    __slots__ = []

    def __init__(self, keyword_class=Keyword, parent=None, keywords=None):
        ItemList.__init__(self, keyword_class, {'parent': parent}, keywords)

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
            if kw.type not in ('setup', 'teardown'):
                yield kw

    def __setitem__(self, index, item):
        old = self[index]
        ItemList.__setitem__(self, index, item)
        self[index]._sort_key = old._sort_key
