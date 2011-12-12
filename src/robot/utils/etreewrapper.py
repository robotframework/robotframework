#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

import os
import sys
from StringIO import StringIO

from robot.errors import DataError


_IRONPYTHON = sys.platform == 'cli'
_ERROR = 'No valid ElementTree XML parser module found'


if not _IRONPYTHON:
    try:
        from xml.etree import cElementTree as ET
    except ImportError:
        try:
            import cElementTree as ET
        except ImportError:
            try:
                from xml.etree import ElementTree as ET
            except ImportError:
                try:
                    from elementtree import ElementTree as ET
                except ImportError:
                    raise ImportError(_ERROR)
else:
    # Cannot use standard ET available on IronPython because it is broken
    # both in 2.7.0 and 2.7.1:
    # http://ironpython.codeplex.com/workitem/31923
    # http://ironpython.codeplex.com/workitem/21407
    try:
        from elementtree import ElementTree as ET
    except ImportError:
        raise ImportError(_ERROR)


class ETSource(object):

    def __init__(self, source):
        self._source = source
        self._opened = None

    def __enter__(self):
        if self._source_file_does_not_exist():
            raise DataError("Source file '%s' does not exist." % self._source)
        self._opened = self._open_source_if_necessary()
        return self._opened or self._source

    def __exit__(self, exc_type, exc_value, exc_trace):
        if self._opened:
            self._opened.close()
        if exc_type is None or exc_type is DataError:
            return False
        raise DataError(exc_value)

    def __str__(self):
        if self._source_is_file_name():
            return self._source
        if hasattr(self._source, 'name'):
            return self._source.name
        return '<in-memory file>'

    def _source_file_does_not_exist(self):
        return self._source_is_file_name() and not os.path.isfile(self._source)

    def _source_is_file_name(self):
        return isinstance(self._source, basestring) \
                and not self._source.startswith('<')

    def _open_source_if_necessary(self):
        if self._source_is_file_name():
            return self._open_source_file()
        if isinstance(self._source, basestring):
            return StringIO(self._source)
        return None

    def _open_source_file(self):
        # File is opened, and later closed, because ElementTree had a bug that
        # it didn't close files it had opened. This caused problems with Jython
        # especially on Windows: http://bugs.jython.org/issue1598
        # The bug has now been fixed in ET and worked around in Jython 2.5.2.
        # File cannot be opened on IronPython, though, as on IronPython ET
        # doesn't handle non-ASCII characters correctly in that case.
        return open(self._source, 'rb') if not _IRONPYTHON else None
