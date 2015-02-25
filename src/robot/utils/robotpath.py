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

import os
import os.path
import sys
import urllib

from robot.errors import DataError

from .encoding import decode_from_system
from .platform import WINDOWS


if WINDOWS:
    CASE_INSENSITIVE_FILESYSTEM = True
else:
    try:
        CASE_INSENSITIVE_FILESYSTEM = os.listdir('/tmp') == os.listdir('/TMP')
    except OSError:
        CASE_INSENSITIVE_FILESYSTEM = False


def normpath(path, case_normalize=False):
    """Replacement for os.path.normpath with some enhancements.

    1. Non-Unicode paths are converted to Unicode using file system encoding.
    2. Optionally lower-case paths on case-insensitive file systems.
       That includes Windows and also OSX in default configuration.
    3. Turn ``c:`` into ``c:\\`` on Windows instead of keeping it as ``c:``.
    """
    if not isinstance(path, unicode):
        path = decode_from_system(path)
    path = os.path.normpath(path)
    if not isinstance(path, unicode):
        # http://bugs.jython.org/issue2274
        path = unicode(path)
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
    4. Handle non-ASCII characters on working directory with Python < 2.6.5:
       http://bugs.python.org/issue3426
    """
    path = normpath(path, case_normalize)
    if os.path.isabs(path):
        return path
    return normpath(os.path.join(os.getcwdu(), path), case_normalize)


# TODO: Investigate could this be replaced with os.path.relpath in RF 2.9.
def get_link_path(target, base):
    """Returns a relative path to a target from a base.

    If base is an existing file, then its parent directory is considered.
    Otherwise, base is assumed to be a directory.

    Rationale: os.path.relpath is not available before Python 2.6
    """
    path =  _get_pathname(target, base)
    url = urllib.pathname2url(path.encode('UTF-8'))
    if os.path.isabs(path):
        url = 'file:' + url
    # At least Jython seems to use 'C|/Path' and not 'C:/Path'
    if os.sep == '\\' and '|/' in url:
        url = url.replace('|/', ':/', 1)
    return url.replace('%5C', '/').replace('%3A', ':').replace('|', ':')

def _get_pathname(target, base):
    target = abspath(target)
    base = abspath(base)
    if os.path.isfile(base):
        base = os.path.dirname(base)
    if base == target:
        return os.path.basename(target)
    base_drive, base_path = os.path.splitdrive(base)
    # if in Windows and base and link on different drives
    if os.path.splitdrive(target)[0] != base_drive:
        return target
    common_len = len(_common_path(base, target))
    if base_path == os.sep:
        return target[common_len:]
    if common_len == len(base_drive) + len(os.sep):
        common_len -= len(os.sep)
    dirs_up = os.sep.join([os.pardir] * base[common_len:].count(os.sep))
    return os.path.join(dirs_up, target[common_len + len(os.sep):])

def _common_path(p1, p2):
    """Returns the longest path common to p1 and p2.

    Rationale: as os.path.commonprefix is character based, it doesn't consider
    path separators as such, so it may return invalid paths:
    commonprefix(('/foo/bar/', '/foo/baz.txt')) -> '/foo/ba' (instead of /foo)
    """
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
    for base in [basedir] + sys.path:
        if not (base and os.path.isdir(base)):
            continue
        if not isinstance(base, unicode):
            base = decode_from_system(base)
        ret = os.path.abspath(os.path.join(base, path))
        if os.path.isfile(ret):
            return ret
        if os.path.isdir(ret) and os.path.isfile(os.path.join(ret, '__init__.py')):
            return ret
    default = file_type or 'File'
    file_type = {'Library': 'Test library',
                 'Variables': 'Variable file',
                 'Resource': 'Resource file'}.get(file_type, default)
    raise DataError("%s '%s' does not exist." % (file_type, path))
