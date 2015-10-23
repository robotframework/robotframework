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

from .robottypes import is_unicode
from .encodingsniffer import get_output_encoding, get_system_encoding
from .unic import unic
from .platform import JYTHON, IRONPYTHON, PY3


OUTPUT_ENCODING = get_output_encoding()
SYSTEM_ENCODING = get_system_encoding()


def decode_output(string, force=False):
    """Decodes bytes from console encoding to Unicode.

    By default returns Unicode strings as-is. `force` argument can be used
    on IronPython where all strings are `unicode` and caller knows decoding
    is needed.
    """
    if is_unicode(string) and not (IRONPYTHON and force):
        return string
    try:
        return string.decode(OUTPUT_ENCODING)
    except UnicodeError:
        return unic(string)


def encode_output(string, errors='replace'):
    """Encodes Unicode to bytes in console encoding."""
    # http://ironpython.codeplex.com/workitem/29487
    if PY3 or IRONPYTHON:
        return string
    return string.encode(OUTPUT_ENCODING, errors)


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
            return string.decode(OUTPUT_ENCODING)
        except UnicodeError:
            return unic(string)

    def encode_to_system(string, errors='replace'):
        """Encodes Unicode to system encoding (e.g. cli args and env vars).

        Non-Unicode values are first converted to Unicode.
        """
        if not is_unicode(string):
            string = unic(string)
        return string.encode(SYSTEM_ENCODING, errors)
