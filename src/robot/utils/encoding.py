#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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
import codecs
from contextlib import contextmanager

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
    """Encodes Unicode to system encoding (e.g. cli args and env vars)."""
    return string.encode(SYSTEM_ENCODING, errors)

# workaround for Python 2.5.0 bug: http://bugs.python.org/issue1586513
@contextmanager
def utf8open(filename, mode='r'):
    file = codecs.open(filename, mode=mode, encoding='utf8')
    try:
        yield file
    finally:
        file.close()
