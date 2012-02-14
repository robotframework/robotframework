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

import sys
import os.path
import codecs

from robot import utils

if utils.is_jython:
    from java.io import FileOutputStream, OutputStreamWriter


class LibraryDocOutput(object):

    def __init__(self, output_path=None):
        self._output_path = output_path
        self._output_file = None

    def __enter__(self):
        if not self._output_path:
            return sys.stdout
        self._output_file = self._create_output_file()
        return self._output_file

    def _create_output_file(self):
        if not utils.is_jython:
            return codecs.open(self._output_path, 'w', 'UTF-8')
        # Java XML APIs cannot handle file opened using codecs.open
        return OutputStreamWriter(FileOutputStream(self._output_path), 'UTF-8')

    def __exit__(self, *exc_info):
        if self._output_file:
            self._output_file.close()
            print os.path.abspath(self._output_path)
