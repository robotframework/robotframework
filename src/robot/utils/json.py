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

import json
from pathlib import Path
from typing import Any, Dict, overload, TextIO

from .error import get_error_message
from .robottypes import type_name

DataDict = Dict[str, Any]


class JsonLoader:
    """Generic JSON loader.

    JSON source can be a string or bytes, a path or an open file object.

    As a special feature handles duplicate items so that lists are merged.
    """

    def load(self, source: "str|bytes|TextIO|Path") -> DataDict:
        try:
            data = self._load(source)
        except (json.JSONDecodeError, TypeError):
            raise ValueError(f"Invalid JSON data: {get_error_message()}")
        if not isinstance(data, dict):
            raise TypeError(f"Expected dictionary, got {type_name(data)}.")
        return data

    def _load(self, source: "str|bytes|TextIO|Path") -> object:
        config = {"object_pairs_hook": self._merge_duplicate_lists}
        if self._is_path(source):
            with open(source, encoding="UTF-8") as file:
                return json.load(file, **config)
        if hasattr(source, "read"):
            return json.load(source, **config)
        return json.loads(source, **config)

    def _merge_duplicate_lists(self, items: "list[tuple[str, object]]") -> dict:
        data = {}
        for name, value in items:
            if name in data and isinstance(value, list):
                data[name].extend(value)
            else:
                data[name] = value
        return data

    def _is_path(self, source: "str|bytes|TextIO|Path") -> bool:
        if isinstance(source, Path):
            return True
        return isinstance(source, str) and "{" not in source


class JsonDumper:
    """Generic JSON dumper.

    JSON can be written to a file given as a path or as an open file object.
    If no output is given, JSON is returned as a string.

    Supports the same configuration as the underlying ``json`` module.
    """

    def __init__(self, **config):
        self.config = config

    @overload
    def dump(self, data: DataDict, output: None = None) -> str: ...

    @overload
    def dump(self, data: DataDict, output: "TextIO|Path|str") -> None: ...

    def dump(self, data: DataDict, output: "None|TextIO|Path|str" = None) -> "None|str":
        if not output:
            return json.dumps(data, **self.config)
        elif isinstance(output, (str, Path)):
            with open(output, "w", encoding="UTF-8") as file:
                json.dump(data, file, **self.config)
            return None
        elif hasattr(output, "write"):
            json.dump(data, output, **self.config)
            return None
        else:
            raise TypeError(
                f"Output should be None, path or open file, got {type_name(output)}."
            )
