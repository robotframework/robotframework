#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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
import os

from unic import unic


def decode_output(string):
    """Decodes string from console encoding to Unicode."""
    if _output_encoding:
        return unic(string, _output_encoding)
    return string

def encode_output(string, errors='replace'):
    """Encodes string from Unicode to console encoding."""
    return string.encode(_output_encoding, errors)


def _get_output_encoding():
    encoding = sys.__stdout__.encoding or sys.__stdin__.encoding
    if os.sep == '/':
        return encoding or _read_encoding_from_env()
    # Use default DOS encoding if no encoding found (guess)
    # or on buggy Jython 2.5: http://bugs.jython.org/issue1568
    if not encoding or sys.platform.startswith('java'):
        return 'cp437'
    return encoding

def _read_encoding_from_env():
    for name in 'LANG', 'LC_CTYPE', 'LANGUAGE', 'LC_ALL':
        if name in os.environ:
            return os.environ[name].split('.')[-1]
    return None

_output_encoding = _get_output_encoding()
