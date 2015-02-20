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

from .dotdict import DotDict
from .platform import IRONPYTHON, JYTHON


def unic(item, *args):
    # Based on a recipe from http://code.activestate.com/recipes/466341
    try:
        return unicode(item, *args)
    except UnicodeError:
        try:
            return u''.join(c if ord(c) < 128 else c.encode('string_escape')
                            for c in str(item))
        except:
            return _unrepresentable_object(item)
    except:
        return _unrepresentable_object(item)


# JVM and .NET seem to handle Unicode normalization automatically. Importing
# unicodedata on Jython also takes some time so it's better to avoid it.
if not (JYTHON or IRONPYTHON):

    from unicodedata import normalize
    _unic = unic

    def unic(item, *args):
        return normalize('NFC', _unic(item, *args))


def prepr(item, width=400):
    return unic(PrettyRepr(width=width).pformat(item))


class PrettyRepr(PrettyPrinter):

    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return repr(object).lstrip('u'), True, False
        if isinstance(object, str):
            return 'b' + repr(object), True, False
        try:
            return PrettyPrinter.format(self, object, context, maxlevels, level)
        except:
            return _unrepresentable_object(object), True, False


def _unrepresentable_object(item):
    from .error import get_error_message
    return u"<Unrepresentable object %s. Error: %s>" \
           % (item.__class__.__name__, get_error_message())
