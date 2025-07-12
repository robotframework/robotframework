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

import os.path
from io import BytesIO, StringIO
from pathlib import Path

from robot.errors import DataError

from .error import get_error_message


def file_writer(path=None, encoding="UTF-8", newline=None, usage=None):
    if not path:
        return StringIO(newline=newline)
    if isinstance(path, Path):
        path = str(path)
    create_destination_directory(path, usage)
    try:
        return open(path, "w", encoding=encoding, newline=newline)
    except EnvironmentError:
        usage = f"{usage} file" if usage else "file"
        raise DataError(f"Opening {usage} '{path}' failed: {get_error_message()}")


def binary_file_writer(path=None):
    if path:
        if isinstance(path, Path):
            path = str(path)
        return open(path, "wb")
    writer = BytesIO()
    getvalue = writer.getvalue
    writer.getvalue = lambda encoding="UTF-8": getvalue().decode(encoding)
    return writer


def create_destination_directory(path: "Path|str", usage=None):
    if not isinstance(path, Path):
        path = Path(path)
    if not path.parent.exists():
        try:
            os.makedirs(path.parent, exist_ok=True)
        except EnvironmentError:
            usage = f"{usage} directory" if usage else "directory"
            raise DataError(
                f"Creating {usage} '{path.parent}' failed: {get_error_message()}"
            )
