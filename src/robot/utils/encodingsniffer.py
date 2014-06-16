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
import os


ANY = True
UNIXY = os.sep == '/'
WINDOWS = not UNIXY
JYTHON = sys.platform.startswith('java')
if UNIXY:
    DEFAULT_SYSTEM_ENCODING = 'UTF-8'
    DEFAULT_OUTPUT_ENCODING = 'UTF-8'
else:
    DEFAULT_SYSTEM_ENCODING = 'cp1252'
    DEFAULT_OUTPUT_ENCODING = 'cp437'


def get_system_encoding():
    platform_getters = [(ANY, _get_python_system_encoding),
                        (JYTHON, _get_java_system_encoding),
                        (UNIXY, _get_unixy_encoding),
                        (WINDOWS, _get_windows_system_encoding)]
    return _get_encoding(platform_getters, DEFAULT_SYSTEM_ENCODING)


def get_output_encoding():
    platform_getters = [(ANY, _get_stream_output_encoding),
                        (UNIXY, _get_unixy_encoding),
                        (WINDOWS, _get_windows_output_encoding)]
    return _get_encoding(platform_getters, DEFAULT_OUTPUT_ENCODING)


def _get_encoding(platform_getters, default):
    for platform, getter in platform_getters:
        if platform:
            encoding = getter()
            if _is_valid(encoding):
                return encoding
    return default


def _get_python_system_encoding():
    return sys.getfilesystemencoding()


def _get_java_system_encoding():
    from java.lang import System
    return System.getProperty('file.encoding')


def _get_unixy_encoding():
    for name in 'LANG', 'LC_CTYPE', 'LANGUAGE', 'LC_ALL':
        if name in os.environ:
            # Encoding can be in format like `UTF-8` or `en_US.UTF-8`
            encoding = os.environ[name].split('.')[-1]
            if _is_valid(encoding):
                return encoding
    return None


def _get_stream_output_encoding():
    # http://bugs.jython.org/issue1568
    if WINDOWS and JYTHON:
        if sys.platform.startswith('java1.5') or sys.version_info < (2, 5, 2):
            return None
    # Stream may not have encoding attribute if it is intercepted outside RF
    # in Python. Encoding is None if process's outputs are redirected.
    for stream in sys.__stdout__, sys.__stderr__, sys.__stdin__:
        encoding = getattr(stream, 'encoding', None)
        if _is_valid(encoding):
            return encoding
    return None


def _get_windows_system_encoding():
    return _get_code_page('GetACP')


def _get_windows_output_encoding():
    return _get_code_page('GetOEMCP')


def _get_code_page(method_name):
    from ctypes import cdll
    try:
        method = getattr(cdll.kernel32, method_name)
    except TypeError:       # Sometimes occurs w/ IronPython (mainly on CI)
        return None
    method.argtypes = ()    # Needed w/ Jython (at least 2.5)
    return 'cp%s' % method()


def _is_valid(encoding):
    if not encoding:
        return False
    try:
        'test'.encode(encoding)
    except LookupError:
        return False
    else:
        return True
