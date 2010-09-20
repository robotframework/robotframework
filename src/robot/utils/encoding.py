#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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
    # Jython is buggy on Windows: http://bugs.jython.org/issue1568
    if os.sep == '\\' and sys.platform.startswith('java'):
        return 'cp437'  # Default DOS encoding
    encoding = _get_encoding_from_std_streams()
    if encoding:
        return encoding
    if os.sep == '/':
        return _read_encoding_from_unix_env()
    return 'cp437'  # Default DOS encoding

def _get_encoding_from_std_streams():
    # Stream may not have encoding attribute if it is intercepted outside RF
    # in Python. Encoding is None if process's outputs are redirected.
    return getattr(sys.__stdout__, 'encoding', None) \
        or getattr(sys.__stderr__, 'encoding', None)

def _read_encoding_from_unix_env():
    for name in 'LANG', 'LC_CTYPE', 'LANGUAGE', 'LC_ALL':
        try:
            # Encoding can be in format like `UTF-8` or `en_US.UTF-8`
            encoding = os.environ[name].split('.')[-1]
            'testing that encoding is valid'.encode(encoding)
        except (KeyError, LookupError):
            pass
        else:
            return encoding
    return 'ascii'

_output_encoding = _get_output_encoding()
