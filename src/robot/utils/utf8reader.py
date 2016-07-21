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

from codecs import BOM_UTF8

from .robottypes import is_string


class Utf8Reader(object):

    def __init__(self, path_or_file):
        if is_string(path_or_file):
            self._file = open(path_or_file, 'rb')
            self._close = True
        else:
            self._file = path_or_file
            self._close = False
        # IronPython handles BOM incorrectly if file not opened in binary mode:
        # https://ironpython.codeplex.com/workitem/34655
        if hasattr(self._file, 'mode') and self._file.mode != 'rb':
            raise ValueError('Only files in binary mode accepted.')

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        if self._close:
            self._file.close()

    def read(self):
        return self._decode(self._file.read())

    def readlines(self):
        for index, line in enumerate(self._file.readlines()):
            yield self._decode(line, remove_bom=index == 0)

    def _decode(self, content, remove_bom=True):
        if remove_bom and content.startswith(BOM_UTF8):
            content = content[len(BOM_UTF8):]
        return content.decode('UTF-8')
