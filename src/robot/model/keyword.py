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

from itertools import chain
from operator import attrgetter

from robot.utils import setter, py2to3

from .itemlist import ItemList
from .modelobject import ModelObject
from .tags import Tags


@py2to3
class Keyword(ModelObject):
    """Base model for a single keyword.

    Extended by :class:`robot.running.model.Keyword` and
    :class:`robot.result.model.Keyword`.
    """
    __slots__ = ['_name', 'doc', 'args', 'assign', 'timeout', 'type',
                 '_teardown', '_sort_key', '_next_child_sort_key']
    KEYWORD_TYPE = 'kw'         #: Normal keyword :attr:`type`.
    SETUP_TYPE = 'setup'        #: Setup :attr:`type`.
    TEARDOWN_TYPE = 'teardown'  #: Teardown :attr:`type`.
    FOR_LOOP_TYPE = 'for'       #: For loop :attr:`type`.
    IF_EXPRESSION_TYPE = 'if'   #: If expression :attr:`type`.
    ELSE_IF_TYPE = "else if"  #: else if branch :attr:`type`.
    ELSE_TYPE = 'else'          #: else branch :attr:`type`.
    FOR_ITEM_TYPE = 'foritem'   #: Single for loop iteration :attr:`type`.

    def __init__(self, name='', doc='', args=(), assign=(), tags=(),
                 timeout=None, type=KEYWORD_TYPE, parent=None):
        self.parent = None
        self.parent = parent
        self._name = name
        self.doc = doc
        self.args = args      #: Keyword arguments as a list of strings.
        self.assign = assign  #: Assigned variables as a list of strings.
        self.tags = tags
        self.timeout = timeout
        #: Keyword type as a string. The value is either :attr:`KEYWORD_TYPE`,
        #: :attr:`SETUP_TYPE`, :attr:`TEARDOWN_TYPE`, :attr:`FOR_LOOP_TYPE` or
        #: :attr:`FOR_ITEM_TYPE` constant defined on the class level.
        self.type = type
        self._teardown = None
        self._sort_key = -1
        self._next_child_sort_key = 0

    def __nonzero__(self):
        return bool(self.name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def teardown(self):
        if self._teardown is None:
            self._teardown = (self.keyword_class or self.__class__)(
                parent=self, type=self.TEARDOWN_TYPE)
        return self._teardown

    @teardown.setter
    def teardown(self, td):
        self._teardown = td

    @setter
    def parent(self, parent):
        """Parent test suite, test case or keyword."""
        if parent and parent is not self.parent:
            self._sort_key = getattr(parent, '_child_sort_key', -1)
        return parent

    @property
    def _child_sort_key(self):
        self._next_child_sort_key += 1
        return self._next_child_sort_key

    @setter
    def tags(self, tags):
        """Keyword tags as a :class:`~.model.tags.Tags` object."""
        return Tags(tags)

    @property
    def id(self):
        """Keyword id in format like ``s1-t3-k1``.

        See :attr:`TestSuite.id <robot.model.testsuite.TestSuite.id>` for
        more information.
        """
        if not self.parent:
            return 'k1'
        if self.parent.keywords:
            return '%s-k%d' % (self.parent.id, self.parent.keywords.index(self)+1)
        fixtures = [kw for kw in (self.parent.setup, self.parent.teardown) if kw]
        return '%s-k%d' % (self.parent.id, fixtures.index(self)+1)

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def reset(self):
        self.__init__(type=self.type)

    def visit(self, visitor):
        """:mod:`Visitor interface <robot.model.visitor>` entry-point."""
        visitor.visit_keyword(self)


class Keywords(ItemList):
    """A list-like object representing keywords in a suite, a test or a keyword.

    Possible setup and teardown keywords are directly available as
    :attr:`setup` and :attr:`teardown` attributes.
    """
    __slots__ = []

    def __init__(self, keyword_class=Keyword, parent=None, keywords=None):
        ItemList.__init__(self, keyword_class, {'parent': parent}, keywords)

    @property
    def setup(self):
        """Keyword used as the setup or ``None`` if no setup.

        Can be set to a new setup keyword or ``None`` since RF 3.0.1.
        """
        return self[0] if (self and self[0].type == 'setup') else None

    @setup.setter
    def setup(self, kw):
        if kw is not None and kw.type != 'setup':
            raise TypeError("Setup keyword type must be 'setup', "
                            "got '%s'." % kw.type)
        if self.setup is not None:
            self.pop(0)
        if kw is not None:
            self.insert(0, kw)

    def create_setup(self, *args, **kwargs):
        self.setup = self._item_class(*args, type='setup', **kwargs)

    @property
    def teardown(self):
        """Keyword used as the teardown or ``None`` if no teardown.

        Can be set to a new teardown keyword or ``None`` since RF 3.0.1.
        """
        return self[-1] if (self and self[-1].type == 'teardown') else None

    @teardown.setter
    def teardown(self, kw):
        if kw is not None and kw.type != 'teardown':
            raise TypeError("Teardown keyword type must be 'teardown', "
                            "got '%s'." % kw.type)
        if self.teardown is not None:
            self.pop()
        if kw is not None:
            self.append(kw)

    def create_teardown(self, *args, **kwargs):
        self.teardown = self._item_class(*args, type='teardown', **kwargs)

    @property
    def all(self):
        """Iterates over all keywords, including setup and teardown."""
        return self

    @property
    def normal(self):
        """Iterates over normal keywords, omitting setup and teardown."""
        kws = [kw for kw in self if kw.type not in ('setup', 'teardown')]
        return Keywords(self._item_class, self._common_attrs['parent'], kws)

    def __setitem__(self, index, item):
        old = self[index]
        ItemList.__setitem__(self, index, item)
        self[index]._sort_key = old._sort_key
