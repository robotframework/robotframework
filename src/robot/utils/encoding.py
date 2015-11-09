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

import sys

from .encodingsniffer import get_output_encoding, get_system_encoding
from .compat import isatty
from .platform import JYTHON, IRONPYTHON, PY3
from .robottypes import is_unicode
from .unic import unic


# TODO: Rename OUTPUT_ENCODING, decode_output, etc. to CONSOLE_ENCODING,
# decode_to_console, etc.

OUTPUT_ENCODING = get_output_encoding()
SYSTEM_ENCODING = get_system_encoding()


def decode_output(string, encoding=OUTPUT_ENCODING, force=False):
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
    encoding = {'CONSOLE': OUTPUT_ENCODING,
                'SYSTEM': SYSTEM_ENCODING}.get(encoding.upper(), encoding)
    try:
        return string.decode(encoding)
    except UnicodeError:
        return unic(string)


def encode_output(string, errors='replace', stream=sys.__stdout__):
    """Encodes Unicode to bytes in console or system encoding.

    Uses console encoding if the given `stream` is a console and system
    encoding otherwise.
    """
    encoding = OUTPUT_ENCODING if isatty(stream) else SYSTEM_ENCODING
    if PY3 and encoding != 'UTF-8':
        return string.encode(encoding, errors).decode(encoding)
    if PY3 or IRONPYTHON:
        return string
    return string.encode(encoding, errors)


# These interpreters handle communication with system APIs using Unicode.
if PY3 or JYTHON or IRONPYTHON:

    def decode_from_system(string):
        return string if is_unicode(string) else unic(string)

    def encode_to_system(string, errors='replace'):
        return string if is_unicode(string) else unic(string)

else:

    def decode_from_system(string):
        """Decodes bytes from system (e.g. cli args or env vars) to Unicode."""
        try:
            return string.decode(SYSTEM_ENCODING)
        except UnicodeError:
            return unic(string)

    def encode_to_system(string, errors='replace'):
        """Encodes Unicode to system encoding (e.g. cli args and env vars).

        Non-Unicode values are first converted to Unicode.
        """
        if not is_unicode(string):
            string = unic(string)
        return string.encode(SYSTEM_ENCODING, errors)
