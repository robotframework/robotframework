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

from robot.utils import file_writer

from .loggerhelper import AbstractLogger
from .loggerapi import LoggerApi


class FileLogger(AbstractLogger, LoggerApi):

    def __init__(self, path, level):
        super().__init__(level)
        self._writer = self._get_writer(path)  # unit test hook

    def _get_writer(self, path):
        return file_writer(path, usage='syslog')

    def message(self, msg):
        if self._is_logged(msg.level) and not self._writer.closed:
            entry = '%s | %s | %s\n' % (msg.timestamp, msg.level.ljust(5),
                                        msg.message)
            self._writer.write(entry)

    def start_suite(self, data, result):
        self.info("Started suite '%s'." % result.name)

    def end_suite(self, data, result):
        self.info("Ended suite '%s'." % result.name)

    def start_test(self, data, result):
        self.info("Started test '%s'." % result.name)

    def end_test(self, data, result):
        self.info("Ended test '%s'." % result.name)

    def start_body_item(self, data, result):
        self.debug(lambda: "Started keyword '%s'." % result.name
                   if result.type in result.KEYWORD_TYPES else result._log_name)

    def end_body_item(self, data, result):
        self.debug(lambda: "Ended keyword '%s'." % result.name
                   if result.type in result.KEYWORD_TYPES else result._log_name)

    def result_file(self, kind, path):
        self.info('%s: %s' % (kind, path))

    def close(self):
        self._writer.close()
