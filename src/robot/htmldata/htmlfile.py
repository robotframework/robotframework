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

from __future__ import with_statement
import os
from os.path import abspath, dirname, join
import codecs
from contextlib import contextmanager


try:
    from org.robotframework.RobotRunner import getResourceAsStream

except ImportError:  # Occurs unless using standalone robotframework.jar

    class HtmlFile(object):
        _base_dir = join(dirname(abspath(__file__)), '..', 'htmldata')

        def __init__(self, filename):
            self._path = join(self._base_dir, filename.replace('/', os.sep))

        def __iter__(self):
            with codecs.open(self._path, encoding='UTF-8') as file:
                for line in file:
                    yield line.rstrip()

else:

    from java.io import BufferedReader, InputStreamReader


    class HtmlFile(object):
        _base_dir = '/Lib/robot/htmldata/'

        def __init__(self, filename):
            self._path = self._base_dir + filename

        def __iter__(self):
            with self._reader as reader:
                line = reader.readLine()
                while line is not None:
                    yield line.rstrip()
                    line = reader.readLine()

        @property
        @contextmanager
        def _reader(self):
            stream = getResourceAsStream(self._path)
            reader = BufferedReader(InputStreamReader(stream, 'UTF-8'))
            try:
                yield reader
            finally:
                reader.close()
