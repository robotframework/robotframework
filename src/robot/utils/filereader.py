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

from io import StringIO
import os.path

from .robottypes import is_bytes, is_pathlike, is_string


class FileReader:
    """Utility to ease reading different kind of files.

    Supports different sources where to read the data:

    - The source can be a path to a file, either as a string or as a
      ``pathlib.Path`` instance in Python 3. The file itself must be
      UTF-8 encoded.

    - Alternatively the source can be an already opened file object,
      including a StringIO or BytesIO object. The file can contain either
      Unicode text or UTF-8 encoded bytes.

    - The third options is giving the source as Unicode text directly.
      This requires setting ``accept_text=True`` when creating the reader.

    In all cases bytes are automatically decoded to Unicode and possible
    BOM removed.
    """

    def __init__(self, source, accept_text=False):
        self.file, self.name, self._opened = self._get_file(source, accept_text)

    def _get_file(self, source, accept_text):
        path = self._get_path(source, accept_text)
        if path:
            file = open(path, 'rb')
            opened = True
        elif is_string(source):
            file = StringIO(source)
            opened = True
        else:
            file = source
            opened = False
        name = getattr(file, 'name', '<in-memory file>')
        return file, name, opened

    def _get_path(self, source, accept_text):
        if is_pathlike(source):
            return str(source)
        if not is_string(source):
            return None
        if not accept_text:
            return source
        if '\n' in source:
            return None
        if os.path.isabs(source) or os.path.exists(source):
            return source
        return None

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        if self._opened:
            self.file.close()

    def read(self):
        return self._decode(self.file.read())

    def readlines(self):
        first_line = True
        for line in self.file.readlines():
            yield self._decode(line, remove_bom=first_line)
            first_line = False

    def _decode(self, content, remove_bom=True):
        if is_bytes(content):
            content = content.decode('UTF-8')
        if remove_bom and content.startswith('\ufeff'):
            content = content[1:]
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
        return content

    def _is_binary_file(self):
        mode = getattr(self.file, 'mode', '')
        encoding = getattr(self.file, 'encoding', 'ascii').lower()
        return 'r' in mode and encoding == 'ascii'
