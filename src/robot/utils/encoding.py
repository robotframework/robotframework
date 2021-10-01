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

import os
import sys

from .encodingsniffer import get_console_encoding, get_system_encoding
from .compat import isatty
from .platform import JYTHON, IRONPYTHON, PY3, PY_VERSION
from .robottypes import is_unicode
from .unic import unic


CONSOLE_ENCODING = get_console_encoding()
SYSTEM_ENCODING = get_system_encoding()
PYTHONIOENCODING = os.getenv('PYTHONIOENCODING')


def console_decode(string, encoding=CONSOLE_ENCODING, force=False):
    """Decodes bytes from console encoding to Unicode.

    By default uses the system console encoding, but that can be configured
    using the `encoding` argument. In addition to the normal encodings,
    it is possible to use case-insensitive values `CONSOLE` and `SYSTEM` to
    use the system console and system encoding, respectively.

    By default returns Unicode strings as-is. The `force` argument can be used
    on IronPython where all strings are `unicode` and caller knows decoding
    is needed.
    """
    if is_unicode(string) and not (IRONPYTHON and force):
        return string
    encoding = {'CONSOLE': CONSOLE_ENCODING,
                'SYSTEM': SYSTEM_ENCODING}.get(encoding.upper(), encoding)
    try:
        return string.decode(encoding)
    except UnicodeError:
        return unic(string)


def console_encode(string, encoding=None, errors='replace', stream=sys.__stdout__,
                   force=False):
    """Encodes Unicode to bytes in console or system encoding.

    If encoding is not given, determines it based on the given stream and system
    configuration. In addition to the normal encodings, it is possible to use
    case-insensitive values `CONSOLE` and `SYSTEM` to use the system console
    and system encoding, respectively.

    On Python 3 and IronPython returns Unicode unless `force` is True in which
    case returns bytes. Otherwise always returns bytes.
    """
    if encoding:
        encoding = {'CONSOLE': CONSOLE_ENCODING,
                    'SYSTEM': SYSTEM_ENCODING}.get(encoding.upper(), encoding)
    else:
        encoding = _get_console_encoding(stream)
    if PY3 and encoding != 'UTF-8':
        encoded = string.encode(encoding, errors)
        return encoded if force else encoded.decode(encoding)
    if (PY3 or IRONPYTHON) and not force:
        return string
    return string.encode(encoding, errors)


def _get_console_encoding(stream):
    encoding = getattr(stream, 'encoding', None)
    if isatty(stream):
        return encoding or CONSOLE_ENCODING
    if PYTHONIOENCODING:
        return PYTHONIOENCODING
    # Jython and IronPython have wrong encoding if outputs are redirected.
    if encoding and not (JYTHON or IRONPYTHON):
        return encoding
    return SYSTEM_ENCODING


# These interpreters handle communication with system APIs using Unicode.
if PY3 or IRONPYTHON or (JYTHON and PY_VERSION < (2, 7, 1)):

    def system_decode(string):
        return string if is_unicode(string) else unic(string)

    def system_encode(string, errors='replace'):
        return string if is_unicode(string) else unic(string)

else:

    # Jython 2.7.1+ uses UTF-8 with cli args etc. regardless the actual system
    # encoding. Cannot set the "real" SYSTEM_ENCODING to that value because
    # we use it also for other purposes.
    _SYSTEM_ENCODING = SYSTEM_ENCODING if not JYTHON else 'UTF-8'

    def system_decode(string):
        """Decodes bytes from system (e.g. cli args or env vars) to Unicode.

        Depending on the usage, at least cli args may already be Unicode.
        """
        if is_unicode(string):
            return string
        try:
            return string.decode(_SYSTEM_ENCODING)
        except UnicodeError:
            return unic(string)

    def system_encode(string, errors='replace'):
        """Encodes Unicode to system encoding (e.g. cli args and env vars).

        Non-Unicode values are first converted to Unicode.
        """
        if not is_unicode(string):
            string = unic(string)
        return string.encode(_SYSTEM_ENCODING, errors)
