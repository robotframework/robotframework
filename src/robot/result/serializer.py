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

from robot.output.xmllogger import XmlLogger


class ResultWriter(XmlLogger):

    def close(self):
        self._writer.end('robot')


class ResultSerializer(object):

    def __init__(self, output):
        self._output = output

    def to_xml(self, suite):
        logger = ResultWriter(self._output)
        suite.visit(logger)
        logger.close()
