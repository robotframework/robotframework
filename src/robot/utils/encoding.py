#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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


def decode_output(string):
    """Decodes bytes from console encoding to Unicode."""
    return unic(string, OUTPUT_ENCODING)

def encode_output(string, errors='replace'):
    """Encodes Unicode to bytes in console encoding."""
    # http://ironpython.codeplex.com/workitem/29487
    if sys.platform == 'cli':
        return string
    return string.encode(OUTPUT_ENCODING, errors)

def decode_from_system(string):
    """Decodes bytes from system (e.g. cli args or env vars) to Unicode."""
    if sys.platform.startswith('java'):
        # http://bugs.jython.org/issue1592
        from java.lang import String
        string = String(string)
    return unic(string, SYSTEM_ENCODING)

def encode_to_system(string):
    """Encodes Unicode to system encoding (e.g. cli args and env vars)."""
    return string.encode(SYSTEM_ENCODING)
