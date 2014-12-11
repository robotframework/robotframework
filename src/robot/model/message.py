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

from robot.utils import html_escape, setter

from .itemlist import ItemList
from .modelobject import ModelObject


class Message(ModelObject):
    """A message outputted during the test execution.

    The message can be a log message triggered by a keyword, or a warning
    or an error occurred during the test execution.
    """
    __slots__ = ['message', 'level', 'html', 'timestamp', 'parent', '_sort_key']

    def __init__(self, message='', level='INFO', html=False, timestamp=None,
                 parent=None):
        #: The message content as a string.
        self.message = message
        #: Severity of the message. Either ``TRACE``, ``INFO``,
        #: ``WARN``, ``DEBUG`` or ``FAIL``/``ERROR``.
        self.level = level
        #: ``True`` if the content is in HTML, ``False`` otherwise.
        self.html = html
        #: Timestamp in format ``%Y%m%d %H:%M:%S.%f``.
        self.timestamp = timestamp
        self._sort_key = -1
        #: The object this message was triggered by.
        self.parent = parent

    @setter
    def parent(self, parent):
        if parent and parent is not getattr(self, 'parent', None):
            self._sort_key = getattr(parent, '_child_sort_key', -1)
        return parent

    @property
    def html_message(self):
        """Returns the message content as HTML."""
        return self.message if self.html else html_escape(self.message)

    def visit(self, visitor):
        visitor.visit_message(self)

    def __unicode__(self):
        return self.message


class Messages(ItemList):
    __slots__ = []

    def __init__(self, message_class=Message, parent=None, messages=None):
        ItemList.__init__(self, message_class, {'parent': parent}, messages)

    def __setitem__(self, index, item):
        old = self[index]
        ItemList.__setitem__(self, index, item)
        self[index]._sort_key = old._sort_key
