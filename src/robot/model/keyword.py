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

import warnings

from robot.utils import setter, py3to2

from .fixture import create_fixture
from .itemlist import ItemList
from .modelobject import ModelObject
from .tags import Tags


@py3to2
class Keyword(ModelObject):
    """Base model for a single keyword.

    Extended by :class:`robot.running.model.Keyword` and
    :class:`robot.result.model.Keyword`.
    """
    __slots__ = ['_name', 'doc', 'args', 'assign', 'timeout', 'type',
                 '_teardown', '_sort_key', '_next_child_sort_key']
    KEYWORD_TYPE  = 'kw'
    SETUP_TYPE    = 'setup'
    TEARDOWN_TYPE = 'teardown'
    FOR_LOOP_TYPE = 'for'
    FOR_ITEM_TYPE = 'foritem'
    IF_TYPE       = 'if'
    ELSE_IF_TYPE  = 'elseif'
    ELSE_TYPE     = 'else'

    def __init__(self, name='', doc='', args=(), assign=(), tags=(),
                 timeout=None, type=KEYWORD_TYPE, parent=None):
        self.parent = parent
        self._name = name
        self.doc = doc
        self.args = args      #: Keyword arguments as a list of strings.
        self.assign = assign  #: Assigned variables as a list of strings.
        self.tags = tags
        self.timeout = timeout
        #: Keyword type as a string. Values defined as constants on the class level.
        self.type = type
        self._teardown = None
        self._sort_key = -1
        self._next_child_sort_key = 0

    def __bool__(self):
        return bool(self.name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property    # Cannot use @setter because it would create teardowns recursively.
    def teardown(self):
        if self._teardown is None:
            self._teardown = create_fixture(None, self, self.TEARDOWN_TYPE)
        return self._teardown

    @teardown.setter
    def teardown(self, teardown):
        self._teardown = create_fixture(teardown, self, self.TEARDOWN_TYPE)

    @setter
    def parent(self, parent):
        """Parent test suite, test case or keyword."""
        if parent and parent is not getattr(self, 'parent', None):
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
        if hasattr(self.parent, 'body') and self.parent.body:
            return '%s-k%d' % (self.parent.id, self.parent.body.index(self)+1)
        fixtures = [kw for kw in (self.parent.setup, self.parent.teardown) if kw]
        return '%s-k%d' % (self.parent.id, fixtures.index(self)+1)

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def visit(self, visitor):
        """:mod:`Visitor interface <robot.model.visitor>` entry-point."""
        visitor.visit_keyword(self)


class Keywords(ItemList):
    """A list-like object representing keywords in a suite, a test or a keyword.

    Deprecated since Robot Framework 4.0.
    """
    __slots__ = []

    def __init__(self, keyword_class=Keyword, parent=None, keywords=None):
        warnings.warn('`keywords` property has been deprecated in Robot Framework 4.0.',
                      UserWarning)
        ItemList.__init__(self, keyword_class, {'parent': parent}, keywords)

    @property
    def setup(self):
        return self[0] if (self and self[0].type == 'setup') else None

    @setup.setter
    def setup(self, kw):
        self.raise_deprecation_error()

    def create_setup(self, *args, **kwargs):
        self.raise_deprecation_error()

    @property
    def teardown(self):
        return self[-1] if (self and self[-1].type == 'teardown') else None

    @teardown.setter
    def teardown(self, kw):
        self.raise_deprecation_error()

    def create_teardown(self, *args, **kwargs):
        self.raise_deprecation_error()

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
        self.raise_deprecation_error()

    def create(self, *args, **kwargs):
        self.raise_deprecation_error()

    def append(self, item):
        self.raise_deprecation_error()

    def extend(self, items):
        self.raise_deprecation_error()

    def insert(self, index, item):
        self.raise_deprecation_error()

    def pop(self, *index):
        self.raise_deprecation_error()

    def remove(self, item):
        self.raise_deprecation_error()

    def clear(self):
        self.raise_deprecation_error()

    def __delitem__(self, index):
        self.raise_deprecation_error()

    def sort(self):
        self.raise_deprecation_error()

    def reverse(self):
        self.raise_deprecation_error()

    @classmethod
    def raise_deprecation_error(cls):
        raise AttributeError('The `keywords` property has been deprecated in RF 4.0. '
                             'Use `body`, `setup` or `teardown` instead.')


class Body(ItemList):
    """A list-like object representing body of a suite, a test or a keyword.

    Body contains the keywords and other structures such as for loops.
    """
    __slots__ = []

    def __init__(self, keyword_class=Keyword, parent=None, keywords=None):
        ItemList.__init__(self, keyword_class, {'parent': parent}, keywords)

    def __setitem__(self, index, item):
        old = self[index]
        ItemList.__setitem__(self, index, item)
        self[index]._sort_key = old._sort_key

    # TODO: add `create_keyword`, `create_for` and `create_if`, deprecate `create`
