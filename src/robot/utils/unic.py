#  Copyright 2008-2015 Nokia Solutions and Networks
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

from pprint import PrettyPrinter

from .platform import IRONPYTHON, JYTHON, PY2
from .robottypes import is_bytes, is_unicode


if PY2:

    def unic(item):
        if isinstance(item, unicode):
            return item
        if isinstance(item, (bytes, bytearray)):
            try:
                return item.decode('ASCII')
            except UnicodeError:
                return u''.join(chr(b) if b < 128 else '\\x%x' % b
                                for b in bytearray(item))
        try:
            try:
                return unicode(item)
            except UnicodeError:
                return unic(str(item))
        except:
            return _unrepresentable_object(item)

else:

    def unic(item):
        if isinstance(item, str):
            return item
        if isinstance(item, (bytes, bytearray)):
            try:
                return item.decode('ASCII')
            except UnicodeError:
                return ''.join(chr(b) if b < 128 else '\\x%x' % b
                               for b in item)
        try:
            return str(item)
        except:
            return _unrepresentable_object(item)


# JVM and .NET seem to handle Unicode normalization automatically. Importing
# unicodedata on Jython also takes some time so it's better to avoid it.
if not (JYTHON or IRONPYTHON):

    from unicodedata import normalize
    _unic = unic

    def unic(item):
        return normalize('NFC', _unic(item))


def prepr(item, width=400):
    return unic(PrettyRepr(width=width).pformat(item))


class PrettyRepr(PrettyPrinter):

    def format(self, object, context, maxlevels, level):
        try:
            if is_unicode(object):
                return repr(object).lstrip('u'), True, False
            if is_bytes(object):
                return 'b' + repr(object).lstrip('b'), True, False
            return PrettyPrinter.format(self, object, context, maxlevels, level)
        except:
            return _unrepresentable_object(object), True, False


def _unrepresentable_object(item):
    from .error import get_error_message
    return u"<Unrepresentable object %s. Error: %s>" \
           % (item.__class__.__name__, get_error_message())
