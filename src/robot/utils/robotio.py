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

import io
import os.path
from pathlib import Path

from robot.errors import DataError

from .error import get_error_message
from .robottypes import is_pathlike


def file_writer(path=None, encoding='UTF-8', newline=None, usage=None):
    if not path:
        return io.StringIO(newline=newline)
    if is_pathlike(path):
        path = str(path)
    create_destination_directory(path, usage)
    try:
        return io.open(path, 'w', encoding=encoding, newline=newline)
    except EnvironmentError:
        usage = '%s file' % usage if usage else 'file'
        raise DataError("Opening %s '%s' failed: %s"
                        % (usage, path, get_error_message()))


def binary_file_writer(path=None):
    if path:
        if is_pathlike(path):
            path = str(path)
        return io.open(path, 'wb')
    f = io.BytesIO()
    getvalue = f.getvalue
    f.getvalue = lambda encoding='UTF-8': getvalue().decode(encoding)
    return f


def create_destination_directory(path: 'Path|str', usage=None):
    if not is_pathlike(path):
        path = Path(path)
    if not path.parent.exists():
        try:
            os.makedirs(path.parent, exist_ok=True)
        except EnvironmentError:
            usage = f'{usage} directory' if usage else 'directory'
            raise DataError(f"Creating {usage} '{path.parent}' failed: "
                            f"{get_error_message()}")
