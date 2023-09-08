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

from datetime import datetime
from typing import Literal

from robot.utils import html_escape, setter

from .body import BodyItem
from .itemlist import ItemList


MessageLevel = Literal['TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FAIL', 'SKIP']


class Message(BodyItem):
    """A message created during the test execution.

    Can be a log message triggered by a keyword, or a warning or an error
    that occurred during parsing or test execution.
    """
    type = BodyItem.MESSAGE
    repr_args = ('message', 'level')
    __slots__ = ['message', 'level', 'html', '_timestamp']

    def __init__(self, message: str = '',
                 level: MessageLevel = 'INFO',
                 html: bool = False,
                 timestamp: 'datetime|str|None' = None,
                 parent: 'BodyItem|None' = None):
        self.message = message
        self.level = level
        self.html = html
        self.timestamp = timestamp
        self.parent = parent

    @setter
    def timestamp(self, timestamp: 'datetime|str|None') -> 'datetime|None':
        if isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp)
        return timestamp

    @property
    def html_message(self):
        """Returns the message content as HTML."""
        return self.message if self.html else html_escape(self.message)

    @property
    def id(self):
        if not self.parent:
            return 'm1'
        messages = self.parent.messages
        index = messages.index(self) if self in messages else len(messages)
        return f'{self.parent.id}-m{index + 1}'

    def visit(self, visitor):
        """:mod:`Visitor interface <robot.model.visitor>` entry-point."""
        visitor.visit_message(self)

    def __str__(self):
        return self.message


class Messages(ItemList):
    __slots__ = []

    def __init__(self, message_class=Message, parent=None, messages=None):
        ItemList.__init__(self, message_class, {'parent': parent}, messages)
