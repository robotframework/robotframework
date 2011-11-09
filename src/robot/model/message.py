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

from modelobject import ModelObject


class Message(ModelObject):
    __slots__ = ['level', 'html', 'timestamp', 'linkable', '_setter__message']

    def __init__(self, message='', level='INFO', html=False, timestamp=None,
                 linkable=False):
        self.message = message
        self.level = level
        self.html = html
        self.timestamp = timestamp
        self.linkable = linkable

    @utils.setter
    def message(self, msg):
        if not isinstance(msg, basestring):
            msg = utils.unic(msg)
        return msg.replace('\r\n', '\n')

    def visit(self, visitor):
        visitor.visit_message(self)

    def __unicode__(self):
        return self.message
