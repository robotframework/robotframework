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
import os


UNIXY = os.sep == '/'
JYTHON = sys.platform.startswith('java')
if UNIXY:
    DEFAULT_SYSTEM_ENCODING = 'UTF-8'
    DEFAULT_OUTPUT_ENCODING = 'UTF-8'
else:
    DEFAULT_SYSTEM_ENCODING = 'cp1252'
    DEFAULT_OUTPUT_ENCODING = 'cp437'


def get_system_encoding():
    encoding = _get_python_file_system_encoding()
    if not encoding and JYTHON:
        encoding = _get_java_file_system_encoding()
    return encoding or DEFAULT_SYSTEM_ENCODING

def _get_python_file_system_encoding():
    encoding = sys.getfilesystemencoding()
    return encoding if _is_valid(encoding) else None

def _get_java_file_system_encoding():
    from java.lang import System
    encoding = System.getProperty('file.encoding')
    return encoding if _is_valid(encoding) else None

def _is_valid(encoding):
    if not encoding:
        return False
    try:
        'test'.encode(encoding)
    except LookupError:
        return False
    else:
        return True


def get_output_encoding():
    if _on_buggy_jython():
        return DEFAULT_OUTPUT_ENCODING
    encoding = _get_encoding_from_standard_streams()
    if not encoding and UNIXY:
        encoding = _get_encoding_from_unix_environment_variables()
    return encoding or DEFAULT_OUTPUT_ENCODING

def _on_buggy_jython():
    # http://bugs.jython.org/issue1568
    if UNIXY or not JYTHON:
        return False
    return sys.platform.startswith('java1.5') or sys.version_info < (2, 5, 2)

def _get_encoding_from_standard_streams():
    # Stream may not have encoding attribute if it is intercepted outside RF
    # in Python. Encoding is None if process's outputs are redirected.
    for stream in sys.__stdout__, sys.__stderr__, sys.__stdin__:
        encoding = getattr(stream, 'encoding', None)
        if _is_valid(encoding):
            return encoding
    return None

def _get_encoding_from_unix_environment_variables():
    for name in 'LANG', 'LC_CTYPE', 'LANGUAGE', 'LC_ALL':
        if name in os.environ:
            # Encoding can be in format like `UTF-8` or `en_US.UTF-8`
            encoding = os.environ[name].split('.')[-1]
            if _is_valid(encoding):
                return encoding
    return None
