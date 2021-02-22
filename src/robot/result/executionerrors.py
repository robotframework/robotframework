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

from robot.model import ItemList, Message
from robot.utils import setter


class ExecutionErrors(object):
    """Represents errors occurred during the execution of tests.

    An error might be, for example, that importing a library has failed.
    """
    id = 'errors'

    def __init__(self, messages=None):
        #: A :class:`list-like object <robot.model.itemlist.ItemList>` of
        #: :class:`~robot.model.message.Message` instances.
        self.messages = messages

    @setter
    def messages(self, messages):
        return ItemList(Message, {'parent': self}, items=messages)

    def add(self, other):
        self.messages.extend(other.messages)

    def visit(self, visitor):
        visitor.visit_errors(self)

    def __iter__(self):
        return iter(self.messages)

    def __len__(self):
        return len(self.messages)

    def __getitem__(self, index):
        return self.messages[index]
