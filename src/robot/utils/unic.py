#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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
import types


if os.name == 'java':
    from java.lang import Object

    def unic(item):
        """Convert non-strings to unicode."""
        if isinstance(item, basestring):
            return item
        if sys.version_info[:2] > (2,2) and isinstance(item, Object):
            item = item.toString()
        return unicode(item)
else:
    def unic(item):
        """Convert non-strings to unicode."""
        typ = type(item)
        if typ is types.UnicodeType:
            return item
        if typ is types.StringType:
            return item.decode('UTF-8', 'ignore')
        return unicode(item)
