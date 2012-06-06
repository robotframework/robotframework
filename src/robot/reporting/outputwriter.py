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

from robot.output.xmllogger import XmlLogger
from robot.result.visitor import ResultVisitor


# TODO: Unify XmlLogger and ResultVisitor APIs.
# Perhaps XmlLogger could be ResultVisitor.


class OutputWriter(XmlLogger, ResultVisitor):

    def __init__(self, output):
        XmlLogger.__init__(self, output, generator='Rebot')

    def start_message(self, msg):
        self._write_message(msg)

    def close(self):
        self._writer.end('robot')
        self._writer.close()

    def start_errors(self, errors):
        XmlLogger.start_errors(self)

    def end_errors(self, errors):
        XmlLogger.end_errors(self)

    def end_result(self, result):
        self.close()

    start_total_statistics = XmlLogger.start_total_stats
    start_tag_statistics = XmlLogger.start_tag_stats
    start_suite_statistics = XmlLogger.start_suite_stats
    end_total_statistics = XmlLogger.end_total_stats
    end_tag_statistics = XmlLogger.end_tag_stats
    end_suite_statistics = XmlLogger.end_suite_stats

    def visit_stat(self, stat):
        self._writer.element('stat', stat.name,
                             stat.get_attributes(values_as_strings=True))
