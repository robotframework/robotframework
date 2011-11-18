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
from StringIO import StringIO

from robot.errors import DataError


class XmlSource(object):

    def __init__(self, source):
        self._source = source
        if isinstance(source, basestring) and not os.path.isfile(source):
            if source.startswith('<'):
                self._source = StringIO(source)
            else:
                raise DataError("Output file '%s' does not exist." % source)

    def __enter__(self):
        return self._source

    def __exit__(self, exc_type, exc_value, exc_trace):
        if exc_type is None or exc_type is DataError:
            return False
        raise DataError(exc_value)

    def __str__(self):
        return str(self._source)

