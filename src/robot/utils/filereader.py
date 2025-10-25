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

from collections.abc import Iterator
from io import StringIO
from pathlib import Path
from typing import TextIO, Union

Source = Union[Path, str, TextIO]


class FileReader:  # FIXME: Rename to SourceReader
    """Utility to ease reading different kind of source files.

    Supports different sources where to read the data:

    - The source can be a path to a file, either as a string or as a
      ``pathlib.Path`` instance. The file itself must be UTF-8 encoded.

    - Alternatively the source can be an already opened file object,
      including a StringIO or BytesIO object. The file can contain either
      Unicode text or UTF-8 encoded bytes.

    - The third options is giving the source as Unicode text directly.
      This requires setting ``accept_text=True`` when creating the reader.

    In all cases bytes are automatically decoded to Unicode and possible
    BOM removed.
    """

    def __init__(self, source: Source, accept_text: bool = False):
        self.file, self._opened = self._get_file(source, accept_text)

    def _get_file(self, source: Source, accept_text: bool) -> "tuple[TextIO, bool]":
        path = self._get_path(source, accept_text)
        if path:
            file = open(path, "rb")
            opened = True
        elif isinstance(source, str):
            file = StringIO(source)
            opened = True
        else:
            file = source
            opened = False
        return file, opened

    def _get_path(self, source: Source, accept_text: bool):
        if isinstance(source, Path):
            return str(source)
        if not isinstance(source, str):
            return None
        if not accept_text:
            return source
        if "\n" in source:
            return None
        path = Path(source)
        try:
            is_path = path.is_absolute() or path.exists()
        except OSError:  # Can happen on Windows w/ Python < 3.10.
            is_path = False
        return source if is_path else None

    @property
    def name(self) -> str:
        return getattr(self.file, "name", "<in-memory file>")

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        if self._opened:
            self.file.close()

    def read(self) -> str:
        return self._decode(self.file.read())

    def readlines(self) -> "Iterator[str]":
        first_line = True
        for line in self.file:
            yield self._decode(line, remove_bom=first_line)
            first_line = False

    def _decode(self, content: "str|bytes", remove_bom: bool = True) -> str:
        if isinstance(content, bytes):
            content = content.decode("UTF-8")
        if remove_bom and content.startswith("\ufeff"):
            content = content[1:]
        if "\r\n" in content:
            content = content.replace("\r\n", "\n")
        return content
