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

from .compat import py2to3
from .platform import IRONPYTHON
from .robottypes import is_string


_ERROR = 'No valid ElementTree XML parser module found'


if not IRONPYTHON:
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
    from StringIO import StringIO


# cElementTree.VERSION seems to always be 1.0.6. We want real API version.
if ET.VERSION < '1.3' and hasattr(ET, 'tostringlist'):
    ET.VERSION = '1.3'


@py2to3
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

    def __unicode__(self):
        if self._source_is_file_name():
            return self._source
        if hasattr(self._source, 'name'):
            return self._source.name
        return '<in-memory file>'

    def _source_is_file_name(self):
        return is_string(self._source) \
                and not self._source.lstrip().startswith('<')

    def _open_source_if_necessary(self):
        if self._source_is_file_name() or not is_string(self._source):
            return None
        if IRONPYTHON:
            return StringIO(self._source)
        return BytesIO(self._source.encode('UTF-8'))
