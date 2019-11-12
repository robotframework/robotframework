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

import errno
import io
import os.path

from robot.errors import DataError

from .error import get_error_message
from .platform import PY3


def file_writer(path=None, encoding='UTF-8', newline=None, usage=None):
    if path:
        create_destination_directory(path, usage)
        try:
            f = io.open(path, 'w', encoding=encoding, newline=newline)
        except EnvironmentError:
            usage = '%s file' % usage if usage else 'file'
            raise DataError("Opening %s '%s' failed: %s"
                            % (usage, path, get_error_message()))
    else:
        f = io.StringIO(newline=newline)
    if PY3:
        return f
    # These streams require written text to be Unicode. We don't want to add
    # `u` prefix to all our strings in Python 2, and cannot really use
    # `unicode_literals` either because many other Python 2 APIs accept only
    # byte strings.
    write = f.write
    f.write = lambda text: write(unicode(text))
    return f


def binary_file_writer(path=None):
    if path:
        return io.open(path, 'wb')
    f = io.BytesIO()
    getvalue = f.getvalue
    f.getvalue = lambda encoding='UTF-8': getvalue().decode(encoding)
    return f


def create_destination_directory(path, usage=None):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        try:
            _makedirs(directory)
        except EnvironmentError:
            usage = '%s directory' % usage if usage else 'directory'
            raise DataError("Creating %s '%s' failed: %s"
                            % (usage, directory, get_error_message()))


def _makedirs(path):
    if PY3:
        os.makedirs(path, exist_ok=True)
    else:
        try:
            os.makedirs(path)
        except OSError as err:
            if err.errno != errno.EEXIST:
                raise
