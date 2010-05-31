#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

from loggerhelper import AbstractLogger


class FileLogger(AbstractLogger):

    def __init__(self, path, level):
        AbstractLogger.__init__(self, level)
        self._writer = self._get_writer(path)

    def _get_writer(self, path):
        # Hook for unittests
        return open(path, 'wb')

    def message(self, msg):
        if self._is_logged(msg.level):
            entry = '%s | %s | %s\n' % (msg.timestamp, msg.level.ljust(5),
                                        msg.message)
            self._writer.write(utils.unic(entry).encode('UTF-8'))

    def start_suite(self, suite):
        self.info("Started test suite '%s'" % suite.name)

    def end_suite(self, suite):
        self.info("Ended test suite '%s'" % suite.name)

    def start_test(self, test):
        self.info("Started test case '%s'" % test.name)

    def end_test(self, test):
        self.info("Ended test case '%s'" % test.name)

    def start_keyword(self, kw):
        self.debug("Started keyword '%s'" % kw.name)

    def end_keyword(self, kw):
        self.debug("Ended keyword '%s'" % kw.name)

    def output_file(self, name, path):
        self.info('%s: %s' % (name, path))

    def close(self):
        self._writer.close()

