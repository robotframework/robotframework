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

from robot.errors import DataError
from robot.utils import file_writer, seq2str2

from .logger import LOGGER
from .loggerhelper import IsLogged


def DebugFile(path):
    if not path:
        LOGGER.info('No debug file')
        return None
    try:
        outfile = file_writer(path, usage='debug')
    except DataError as err:
        LOGGER.error(err.message)
        return None
    else:
        LOGGER.info('Debug file: %s' % path)
        return _DebugFileWriter(outfile)


class _DebugFileWriter:
    _separators = {'SUITE': '=', 'TEST': '-', 'KEYWORD': '~'}

    def __init__(self, outfile):
        self._indent = 0
        self._kw_level = 0
        self._separator_written_last = False
        self._outfile = outfile
        self._is_logged = IsLogged('DEBUG')

    def start_suite(self, suite):
        self._separator('SUITE')
        self._start('SUITE', suite.longname, suite.start_time)
        self._separator('SUITE')

    def end_suite(self, suite):
        self._separator('SUITE')
        self._end('SUITE', suite.longname, suite.end_time, suite.elapsed_time)
        self._separator('SUITE')
        if self._indent == 0:
            LOGGER.output_file('Debug', self._outfile.name)
            self.close()

    def start_test(self, test):
        self._separator('TEST')
        self._start('TEST', test.name, test.start_time)
        self._separator('TEST')

    def end_test(self, test):
        self._separator('TEST')
        self._end('TEST', test.name, test.end_time, test.elapsed_time)
        self._separator('TEST')

    def start_keyword(self, kw):
        if self._kw_level == 0:
            self._separator('KEYWORD')
        self._start(kw.type, kw.name, kw.start_time, seq2str2(kw.args))
        self._kw_level += 1

    def end_keyword(self, kw):
        self._end(kw.type, kw.name, kw.end_time, kw.elapsed_time)
        self._kw_level -= 1

    def log_message(self, msg):
        if self._is_logged(msg.level):
            self._write(f'{msg.timestamp} - {msg.level} - {msg.message}')

    def close(self):
        if not self._outfile.closed:
            self._outfile.close()

    def _start(self, type, name, timestamp, extra=''):
        if extra:
            extra = f' {extra}'
        indent = '-' * self._indent
        self._write(f'{timestamp} - INFO - +{indent} START {type}: {name}{extra}')
        self._indent += 1

    def _end(self, type, name, timestamp, elapsed):
        self._indent -= 1
        indent = '-' * self._indent
        elapsed = elapsed.total_seconds()
        self._write(f'{timestamp} - INFO - +{indent} END {type}: {name} ({elapsed} s)')

    def _separator(self, type_):
        self._write(self._separators[type_] * 78, separator=True)

    def _write(self, text, separator=False):
        if separator and self._separator_written_last:
            return
        self._outfile.write(text.rstrip() + '\n')
        self._outfile.flush()
        self._separator_written_last = separator
