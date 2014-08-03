#  Copyright 2008-2014 Nokia Solutions and Networks
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
from .unic import unic


OUTPUT_ENCODING = get_output_encoding()
SYSTEM_ENCODING = get_system_encoding()


def decode_output(string, force=False):
    """Decodes bytes from console encoding to Unicode.

    By default returns Unicode strings as-is. `force` argument can be used
    on IronPython where all strings are `unicode` and caller knows decoding
    is needed.
    """
    if isinstance(string, unicode) and not force:
        return string
    return unic(string, OUTPUT_ENCODING)


def encode_output(string, errors='replace'):
    """Encodes Unicode to bytes in console encoding."""
    # http://ironpython.codeplex.com/workitem/29487
    if sys.platform == 'cli':
        return string
    return string.encode(OUTPUT_ENCODING, errors)


def decode_from_system(string, can_be_from_java=True):
    """Decodes bytes from system (e.g. cli args or env vars) to Unicode."""
    if sys.platform == 'cli':
        return string
    if sys.platform.startswith('java') and can_be_from_java:
        # http://bugs.jython.org/issue1592
        from java.lang import String
        string = String(string)
    return unic(string, SYSTEM_ENCODING)


def encode_to_system(string, errors='replace'):
    """Encodes Unicode to system encoding (e.g. cli args and env vars).

    Non-Unicode strings are first converted to Unicode.
    """
    if not isinstance(string, unicode):
        string = unicode(string)
    return string.encode(SYSTEM_ENCODING, errors)
