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

from robot.errors import DataError

from .loggerhelper import AbstractLogger


class FileLogger(AbstractLogger):

    def __init__(self, path, level):
        AbstractLogger.__init__(self, level)
        self._writer = self._get_writer(path)  # unit test hook

    def _get_writer(self, path):
        try:
            return open(path, 'w')
        except EnvironmentError, err:
            raise DataError(err.strerror)

    def message(self, msg):
        if self._is_logged(msg.level) and not self._writer.closed:
            entry = '%s | %s | %s\n' % (msg.timestamp, msg.level.ljust(5),
                                        msg.message)
            self._writer.write(entry.encode('UTF-8'))

    def start_suite(self, suite):
        self.info("Started test suite '%s'" % suite.name)

    def end_suite(self, suite):
        self.info("Ended test suite '%s'" % suite.name)

    def start_test(self, test):
        self.info("Started test case '%s'" % test.name)

    def end_test(self, test):
        self.info("Ended test case '%s'" % test.name)

    def start_keyword(self, kw):
        self.debug(lambda: "Started keyword '%s'" % kw.name)

    def end_keyword(self, kw):
        self.debug(lambda: "Ended keyword '%s'" % kw.name)

    def output_file(self, name, path):
        self.info('%s: %s' % (name, path))

    def close(self):
        self._writer.close()
