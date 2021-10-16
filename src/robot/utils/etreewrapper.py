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

from io import BytesIO
from os import fsdecode
import re

from .robottypes import is_bytes, is_pathlike, is_string

try:
    from xml.etree import cElementTree as ET
except ImportError:
    try:
        from xml.etree import ElementTree as ET
    except ImportError:
        raise ImportError('No valid ElementTree XML parser module found')


class ETSource:

    def __init__(self, source):
        self._source = source
        self._opened = None

    def __enter__(self):
        self._opened = self._open_if_necessary(self._source)
        return self._opened or self._source

    def _open_if_necessary(self, source):
        if self._is_path(source) or self._is_already_open(source):
            return None
        if is_bytes(source):
            return BytesIO(source)
        encoding = self._find_encoding(source)
        return BytesIO(source.encode(encoding))

    def _is_path(self, source):
        if is_pathlike(source):
            return True
        elif is_string(source):
            prefix = '<'
        elif is_bytes(source):
            prefix = b'<'
        else:
            return False
        return not source.lstrip().startswith(prefix)

    def _is_already_open(self, source):
        return not (is_string(source) or is_bytes(source))

    def _find_encoding(self, source):
        match = re.match(r"\s*<\?xml .*encoding=(['\"])(.*?)\1.*\?>", source)
        return match.group(2) if match else 'UTF-8'

    def __exit__(self, exc_type, exc_value, exc_trace):
        if self._opened:
            self._opened.close()

    def __str__(self):
        source = self._source
        if self._is_path(source):
            return self._path_to_string(source)
        if hasattr(source, 'name'):
            return self._path_to_string(source.name)
        return '<in-memory file>'

    def _path_to_string(self, path):
        if is_pathlike(path):
            return str(path)
        if is_bytes(path):
            return fsdecode(path)
        return path
