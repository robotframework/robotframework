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
import locale

from .misc import isatty
from .platform import UNIXY, WINDOWS


if UNIXY:
    DEFAULT_CONSOLE_ENCODING = 'UTF-8'
    DEFAULT_SYSTEM_ENCODING = 'UTF-8'
else:
    DEFAULT_CONSOLE_ENCODING = 'cp437'
    DEFAULT_SYSTEM_ENCODING = 'cp1252'


def get_system_encoding():
    platform_getters = [(True, _get_python_system_encoding),
                        (UNIXY, _get_unixy_encoding),
                        (WINDOWS, _get_windows_system_encoding)]
    return _get_encoding(platform_getters, DEFAULT_SYSTEM_ENCODING)


def get_console_encoding():
    platform_getters = [(True, _get_stream_output_encoding),
                        (UNIXY, _get_unixy_encoding),
                        (WINDOWS, _get_windows_console_encoding)]
    return _get_encoding(platform_getters, DEFAULT_CONSOLE_ENCODING)


def _get_encoding(platform_getters, default):
    for platform, getter in platform_getters:
        if platform:
            encoding = getter()
            if _is_valid(encoding):
                return encoding
    return default


def _get_python_system_encoding():
    # ValueError occurs with PyPy 3.10 if language config is invalid.
    # https://foss.heptapod.net/pypy/pypy/-/issues/3975
    try:
        return locale.getpreferredencoding(False)
    except ValueError:
        return None


def _get_unixy_encoding():
    # Cannot use `locale.getdefaultlocale()` because it is deprecated.
    # Using same environment variables here anyway.
    # https://docs.python.org/3/library/locale.html#locale.getdefaultlocale
    for name in 'LC_ALL', 'LC_CTYPE', 'LANG', 'LANGUAGE':
        if name in os.environ:
            # Encoding can be in format like `UTF-8` or `en_US.UTF-8`
            encoding = os.environ[name].split('.')[-1]
            if _is_valid(encoding):
                return encoding
    return None


def _get_stream_output_encoding():
    # Python 3.6+ uses UTF-8 as encoding with output streams.
    # We want the real console encoding regardless the platform.
    if WINDOWS:
        return None
    for stream in sys.__stdout__, sys.__stderr__, sys.__stdin__:
        if isatty(stream):
            encoding = getattr(stream, 'encoding', None)
            if _is_valid(encoding):
                return encoding
    return None


def _get_windows_system_encoding():
    return _get_code_page('GetACP')


def _get_windows_console_encoding():
    return _get_code_page('GetConsoleOutputCP')


def _get_code_page(method_name):
    from ctypes import cdll
    method = getattr(cdll.kernel32, method_name)
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
