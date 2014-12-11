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

from robot.output.xmllogger import XmlLogger


class OutputWriter(XmlLogger):

    def __init__(self, output):
        XmlLogger.__init__(self, output, generator='Rebot')

    def start_message(self, msg):
        self._write_message(msg)

    def visit_keyword(self, kw):
        self.start_keyword(kw)
        for child in kw.children:
            child.visit(self)
        self.end_keyword(kw)

    def close(self):
        self._writer.end('robot')
        self._writer.close()

    def end_result(self, result):
        self.close()
