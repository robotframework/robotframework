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

import sys


def unic(item, *args):
    # Based on a recipe from http://code.activestate.com/recipes/466341
    try:
        return unicode(item, *args)
    except UnicodeDecodeError:
        ascii_text = str(item).encode('string_escape')
        return unicode(ascii_text)


if sys.platform.startswith('java'):
    from java.lang import Object, Class
    _unic = unic

    def unic(item, *args):
        if isinstance(item, basestring) and not args:
            return item
        if isinstance(item, Object) and not isinstance(item, Class): # http://bugs.jython.org/issue1564
            item = item.toString()  # http://bugs.jython.org/issue1563
        return _unic(item, *args)
