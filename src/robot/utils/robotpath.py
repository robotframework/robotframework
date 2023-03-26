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
import os.path
import sys
from urllib.request import pathname2url as path_to_url

from robot.errors import DataError

from .encoding import system_decode
from .platform import WINDOWS
from .robottypes import is_string
from .unic import safe_str


if WINDOWS:
    CASE_INSENSITIVE_FILESYSTEM = True
else:
    try:
        CASE_INSENSITIVE_FILESYSTEM = os.listdir('/tmp') == os.listdir('/TMP')
    except OSError:
        CASE_INSENSITIVE_FILESYSTEM = False


def normpath(path, case_normalize=False):
    """Replacement for os.path.normpath with some enhancements.

    1. Convert non-Unicode paths to Unicode using the file system encoding.
    2. NFC normalize Unicode paths (affects mainly OSX).
    3. Optionally lower-case paths on case-insensitive file systems.
       That includes Windows and also OSX in default configuration.
    4. Turn ``c:`` into ``c:\\`` on Windows instead of keeping it as ``c:``.
    """
    if not is_string(path):
        path = system_decode(path)
    path = safe_str(path)  # Handles NFC normalization on OSX
    path = os.path.normpath(path)
    if case_normalize and CASE_INSENSITIVE_FILESYSTEM:
        path = path.lower()
    if WINDOWS and len(path) == 2 and path[1] == ':':
        return path + '\\'
    return path


def abspath(path, case_normalize=False):
    """Replacement for os.path.abspath with some enhancements and bug fixes.

    1. Non-Unicode paths are converted to Unicode using file system encoding.
    2. Optionally lower-case paths on case-insensitive file systems.
       That includes Windows and also OSX in default configuration.
    3. Turn ``c:`` into ``c:\\`` on Windows instead of ``c:\\current\\path``.
    """
    path = normpath(path, case_normalize)
    return normpath(os.path.abspath(path), case_normalize)


def get_link_path(target, base):
    """Returns a relative path to ``target`` from ``base``.

    If ``base`` is an existing file, then its parent directory is considered to
    be the base. Otherwise ``base`` is assumed to be a directory.

    The returned path is URL encoded. On Windows returns an absolute path with
    ``file:`` prefix if the target is on a different drive.
    """
    path = _get_link_path(target, base)
    url = path_to_url(path)
    if os.path.isabs(path):
        url = 'file:' + url
    return url


def _get_link_path(target, base):
    target = abspath(target)
    base = abspath(base)
    if os.path.isfile(base):
        base = os.path.dirname(base)
    if base == target:
        return '.'
    base_drive, base_path = os.path.splitdrive(base)
    # Target and base on different drives
    if os.path.splitdrive(target)[0] != base_drive:
        return target
    common_len = len(_common_path(base, target))
    if base_path == os.sep:
        return target[common_len:]
    if common_len == len(base_drive) + len(os.sep):
        common_len -= len(os.sep)
    dirs_up = os.sep.join([os.pardir] * base[common_len:].count(os.sep))
    path = os.path.join(dirs_up, target[common_len + len(os.sep):])
    return os.path.normpath(path)


def _common_path(p1, p2):
    """Returns the longest path common to p1 and p2.

    Rationale: as os.path.commonprefix is character based, it doesn't consider
    path separators as such, so it may return invalid paths:
    commonprefix(('/foo/bar/', '/foo/baz.txt')) -> '/foo/ba' (instead of /foo)
    """
    # os.path.dirname doesn't normalize leading double slash
    # https://github.com/robotframework/robotframework/issues/3844
    if p1.startswith('//'):
        p1 = '/' + p1.lstrip('/')
    if p2.startswith('//'):
        p2 = '/' + p2.lstrip('/')
    while p1 and p2:
        if p1 == p2:
            return p1
        if len(p1) > len(p2):
            p1 = os.path.dirname(p1)
        else:
            p2 = os.path.dirname(p2)
    return ''


def find_file(path, basedir='.', file_type=None):
    path = os.path.normpath(path.replace('/', os.sep))
    if os.path.isabs(path):
        ret = _find_absolute_path(path)
    else:
        ret = _find_relative_path(path, basedir)
    if ret:
        return ret
    raise DataError(f"{file_type or 'File'} '{path}' does not exist.")


def _find_absolute_path(path):
    if _is_valid_file(path):
        return path
    return None


def _find_relative_path(path, basedir):
    for base in [basedir] + sys.path:
        if not (base and os.path.isdir(base)):
            continue
        if not is_string(base):
            base = system_decode(base)
        ret = os.path.abspath(os.path.join(base, path))
        if _is_valid_file(ret):
            return ret
    return None


def _is_valid_file(path):
    return os.path.isfile(path) or \
        (os.path.isdir(path) and os.path.isfile(os.path.join(path, '__init__.py')))
