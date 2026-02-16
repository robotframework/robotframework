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

import re
from io import BytesIO
from os import fsdecode
from pathlib import Path
from typing import IO, Union

Source = Union[IO, Path, str, bytes, bytearray]


class ETSource:

    def __init__(self, source: Source):
        self._source = source
        self._opened: "BytesIO | None" = None

    def __enter__(self) -> "IO | Path | str | bytes":
        self._opened = self._open_if_necessary(self._source)
        return self._opened or self._source

    def _open_if_necessary(self, source: Source) -> "BytesIO | None":
        if self._is_path(source) or self._is_already_open(source):
            return None
        if isinstance(source, (bytes, bytearray)):
            return BytesIO(source)
        encoding = self._find_encoding(source)
        return BytesIO(source.encode(encoding))

    def _is_path(self, source: Source) -> bool:
        if isinstance(source, Path):
            return True
        if isinstance(source, str):
            return not source.lstrip().startswith("<")
        if isinstance(source, bytes):
            return not source.lstrip().startswith(b"<")
        return False

    def _is_already_open(self, source: Source) -> bool:
        return not isinstance(source, (str, bytes, bytearray))

    def _find_encoding(self, source: str) -> str:
        match = re.match(r"\s*<\?xml .*encoding=(['\"])(.*?)\1.*\?>", source)
        return match.group(2) if match else "UTF-8"

    def __exit__(self, exc_type, exc_value, exc_trace):
        if self._opened:
            self._opened.close()

    def __str__(self) -> str:
        source = self._source
        if self._is_path(source):
            return self._path_to_string(source)
        if hasattr(source, "name"):
            return self._path_to_string(source.name)
        return "<in-memory file>"

    def _path_to_string(self, path: "Path | str | bytes") -> str:
        if isinstance(path, Path):
            return str(path)
        if isinstance(path, bytes):
            return fsdecode(path)
        return path
