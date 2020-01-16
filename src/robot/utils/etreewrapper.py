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
import re

from .compat import py2to3
from .platform import IRONPYTHON, PY_VERSION, PY3
from .robottypes import is_bytes, is_pathlike, is_string

if PY3:
    from os import fsdecode
else:
    from .encoding import console_decode as fsdecode


IRONPYTHON_WITH_BROKEN_ETREE = IRONPYTHON and PY_VERSION < (2, 7, 9)
NO_ETREE_ERROR = 'No valid ElementTree XML parser module found'


if not IRONPYTHON_WITH_BROKEN_ETREE:
    try:
        from xml.etree import cElementTree as ET
    except ImportError:
        try:
            from xml.etree import ElementTree as ET
        except ImportError:
            raise ImportError(NO_ETREE_ERROR)
else:
    # Standard ElementTree works only with IronPython 2.7.9+
    # https://github.com/IronLanguages/ironpython2/issues/370
    try:
        from elementtree import ElementTree as ET
    except ImportError:
        raise ImportError(NO_ETREE_ERROR)
    from StringIO import StringIO


# cElementTree.VERSION seems to always be 1.0.6. We want real API version.
if ET.VERSION < '1.3' and hasattr(ET, 'tostringlist'):
    ET.VERSION = '1.3'


@py2to3
class ETSource(object):

    def __init__(self, source):
        # ET on Python < 3.6 doesn't support pathlib.Path
        if PY_VERSION < (3, 6) and is_pathlike(source):
            source = str(source)
        self._source = source
        self._opened = None

    def __enter__(self):
        self._opened = self._open_if_necessary(self._source)
        return self._opened or self._source

    def _open_if_necessary(self, source):
        if self._is_path(source) or self._is_already_open(source):
            return None
        if IRONPYTHON_WITH_BROKEN_ETREE:
            return StringIO(source)
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
        match = re.match("\s*<\?xml .*encoding=(['\"])(.*?)\\1.*\?>", source)
        return match.group(2) if match else 'UTF-8'

    def __exit__(self, exc_type, exc_value, exc_trace):
        if self._opened:
            self._opened.close()

    def __unicode__(self):
        source = self._source
        if self._is_path(source):
            return self._path_to_string(source)
        if hasattr(source, 'name'):
            return self._path_to_string(source.name)
        return u'<in-memory file>'

    def _path_to_string(self, path):
        if is_pathlike(path):
            return str(path)
        if is_bytes(path):
            return fsdecode(path)
        return path
