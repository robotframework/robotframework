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

import sys
import os.path
from StringIO import StringIO


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


# cElementTree.VERSION seems to always be 1.0.6. We want real API version.
if ET.VERSION < '1.3' and hasattr(ET, 'tostringlist'):
    ET.VERSION = '1.3'


class ETSource(object):

    def __init__(self, source):
        self._source = source
        self._opened = None

    def __enter__(self):
        self._opened = self._open_source_if_necessary()
        return self._opened or self._source

    def __exit__(self, exc_type, exc_value, exc_trace):
        if self._opened:
            self._opened.close()

    def __str__(self):
        if self._source_is_file_name():
            return self._source
        if hasattr(self._source, 'name'):
            return self._source.name
        return '<in-memory file>'

    def _source_is_file_name(self):
        return isinstance(self._source, basestring) \
                and not self._source.lstrip().startswith('<')

    def _open_source_if_necessary(self):
        if self._source_is_file_name():
            return self._open_file(self._source)
        if isinstance(self._source, basestring):
            return self._open_string_io(self._source)
        return None

    if not _IRONPYTHON:

        # File is opened, and later closed, because ElementTree had a bug that
        # it didn't close files it had opened. This caused problems with Jython
        # especially on Windows: http://bugs.jython.org/issue1598
        # The bug has now been fixed in ET and worked around in Jython 2.5.2.
        def _open_file(self, source):
            return open(source, 'rb')

        def _open_string_io(self, source):
            return StringIO(source.encode('UTF-8'))

    else:

        # File cannot be opened on IronPython, however, as ET does not seem to
        # handle non-ASCII characters correctly in that case. We want to check
        # that the file exists even in that case, though.
        def _open_file(self, source):
            if not os.path.exists(source):
                raise IOError(2, 'No such file', source)
            return None

        def _open_string_io(self, source):
            return StringIO(source)
