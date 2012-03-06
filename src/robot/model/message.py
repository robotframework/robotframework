#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

from robot.utils import html_escape

from .itemlist import ItemList
from .modelobject import ModelObject


class Message(ModelObject):
    __slots__ = ['message', 'level', 'html', 'timestamp', 'parent']

    def __init__(self, message='', level='INFO', html=False, timestamp=None,
                 parent=None):
        self.message = message
        self.level = level
        self.html = html
        self.timestamp = timestamp
        self.parent = parent

    @property
    def html_message(self):
        return self.message if self.html else html_escape(self.message)

    def visit(self, visitor):
        visitor.visit_message(self)

    def __unicode__(self):
        return self.message


class Messages(ItemList):
    __slots__ = []

    def __init__(self, message_class=Message, parent=None, messages=None):
        ItemList.__init__(self, message_class, {'parent': parent}, messages)

