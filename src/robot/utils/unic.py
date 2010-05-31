#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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


if sys.platform.startswith('java'):
    from java.lang import Object, Class

    def unic(item, *args):
        # http://bugs.jython.org/issue1564
        if isinstance(item, Object) and not isinstance(item, Class):
            item = item.toString()  # http://bugs.jython.org/issue1563
        return _unic(item, *args)

else:
    # importing unicodedata on jython takes a very long time, and does not seem 
    # necessary as java probably already handles normalization. Furthermore 
    # java 1.5 does not even have unicodedata.normalize
    from unicodedata import normalize
    
    def unic(item, *args):
        return normalize('NFC', _unic(item, *args))


def _unic(item, *args):
    # Based on a recipe from http://code.activestate.com/recipes/466341
    try:
        return unicode(item, *args)
    except UnicodeError:
        try:
            ascii_text = str(item).encode('string_escape')
        except UnicodeError:
            return u"<unrepresentable object '%s'>" % item.__class__.__name__
        else:
            return unicode(ascii_text)


def safe_repr(item):
    try:
        return unic(repr(item))
    except UnicodeError:
        return repr(unic(item))
