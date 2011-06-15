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

from __future__ import with_statement
from robot.result.elementhandlers import RootHandler, Context
from robot.result.jsondatamodel import DataModel
import xml.sax as sax
from xml.sax.handler import ContentHandler

def create_datamodel_from(input_filename):
    robot = _RobotOutputHandler(Context())
    with open(input_filename, 'r') as input:
        sax.parse(input, robot)
    return robot.datamodel


def parse_js(input_filename, output):
    create_datamodel_from(input_filename).write_to(output)


class _RobotOutputHandler(ContentHandler):

    def __init__(self, context):
        self._context = context
        self._root_handler = RootHandler(context)
        self._handler_stack = [self._root_handler]

    @property
    def datamodel(self):
        return DataModel(self._root_handler.data)

    def startElement(self, name, attrs):
        handler = self._handler_stack[-1].get_handler_for(name, attrs)
        self._charbuffer = []
        self._handler_stack.append(handler)

    def endElement(self, name):
        handler = self._handler_stack.pop()
        self._handler_stack[-1].add_child_data(handler.end_element(self.text))

    def characters(self, content):
        self._charbuffer += [content]

    @property
    def text(self):
        return ''.join(self._charbuffer)

