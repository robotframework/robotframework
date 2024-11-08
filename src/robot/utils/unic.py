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

import sys
from pprint import PrettyPrinter
from unicodedata import normalize


def safe_str(item):
    return normalize('NFC', _safe_str(item))


def _safe_str(item):
    if isinstance(item, str):
        return item
    if isinstance(item, (bytes, bytearray)):
        # Map each byte to Unicode code point with same ordinal.
        return item.decode('latin-1')
    try:
        return str(item)
    except Exception:
        return _unrepresentable_object(item)


def prepr(item, width=80, sort_dicts=False):
    return safe_str(PrettyRepr(width=width, sort_dicts=sort_dicts).pformat(item))


class PrettyRepr(PrettyPrinter):

    def format(self, object, context, maxlevels, level):
        try:
            return PrettyPrinter.format(self, object, context, maxlevels, level)
        except Exception:
            return _unrepresentable_object(object), True, False

    # Don't split strings: https://stackoverflow.com/questions/31485402
    def _format(self, object, *args, **kwargs):
        if isinstance(object, (str, bytes, bytearray)):
            width = self._width
            self._width = sys.maxsize
            try:
                super()._format(object, *args, **kwargs)
            finally:
                self._width = width
        else:
            super()._format(object, *args, **kwargs)


def _unrepresentable_object(item):
    from .error import get_error_message

    error = get_error_message()
    return f'<Unrepresentable object {type(item).__name__}. Error: {error}>'
