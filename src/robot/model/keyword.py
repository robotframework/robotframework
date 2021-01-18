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

from robot.utils import setter, py3to2, unicode

from .body import Body, BodyItem
from .fixture import create_fixture
from .itemlist import ItemList
from .tags import Tags


@py3to2
@Body.register
class Keyword(BodyItem):
    """Base model for a single keyword.

    Extended by :class:`robot.running.model.Keyword` and
    :class:`robot.result.model.Keyword`.
    """
    repr_args = ('name', 'args', 'assign')
    __slots__ = ['_name', 'doc', 'args', 'assign', 'timeout', 'type', '_teardown']

    def __init__(self, name='', doc='', args=(), assign=(), tags=(),
                 timeout=None, type=BodyItem.KEYWORD_TYPE, parent=None):
        self._name = name
        self.doc = doc
        self.args = args
        self.assign = assign
        self.tags = tags
        self.timeout = timeout
        self.type = type
        self._teardown = None
        self.parent = parent

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property    # Cannot use @setter because it would create teardowns recursively.
    def teardown(self):
        if self._teardown is None and self:
            self._teardown = create_fixture(None, self, self.TEARDOWN_TYPE)
        return self._teardown

    @teardown.setter
    def teardown(self, teardown):
        self._teardown = create_fixture(teardown, self, self.TEARDOWN_TYPE)

    @setter
    def tags(self, tags):
        """Keyword tags as a :class:`~.model.tags.Tags` object."""
        return Tags(tags)

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    def visit(self, visitor):
        """:mod:`Visitor interface <robot.model.visitor>` entry-point."""
        if self:
            visitor.visit_keyword(self)

    def __bool__(self):
        return self.name is not None

    def __str__(self):
        parts = list(self.assign) + [self.name] + list(self.args)
        return '    '.join(unicode(p) for p in parts)


class Keywords(ItemList):
    """A list-like object representing keywords in a suite, a test or a keyword.

    Read-only and deprecated since Robot Framework 4.0.
    """
    __slots__ = []
    deprecation_message = (
        "'keywords' attribute is read-only and deprecated since Robot Framework 4.0. "
        "Use 'body', 'setup' or 'teardown' instead."
    )

    def __init__(self, parent=None, keywords=None):
        warnings.warn(self.deprecation_message, UserWarning)
        ItemList.__init__(self, object, {'parent': parent})
        if keywords:
            ItemList.extend(self, keywords)

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
        return [kw for kw in self if kw.type not in ('setup', 'teardown')]

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
        raise AttributeError(cls.deprecation_message)
