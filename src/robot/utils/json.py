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
from typing import Dict, overload, TextIO

from .error import get_error_message
from .robottypes import type_name

DataDict = Dict[str, object]


class JsonLoader:
    """Generic JSON object loader.

    JSON source can be a string or bytes, a path or an open file object.
    The top level JSON item must always be a dictionary.

    Supports the same configuration parameters as the underlying  `json.load`__
    except for ``object_pairs_hook``. As a special feature, handles duplicate
    items so that lists are merged.

    __ https://docs.python.org/3/library/json.html#json.load
    """

    def __init__(self, **config):
        self.config = self._add_hook_to_merge_duplicate_lists(config)

    def _add_hook_to_merge_duplicate_lists(self, config):
        object_hook = config.get("object_hook")
        object_pairs_hook = config.get("object_pairs_hook")
        if object_pairs_hook:
            raise ValueError("'object_pairs_hook' is not supported.")

        def merge_duplicate_lists(items: "list[tuple[str, object]]") -> DataDict:
            data = {}
            for name, value in items:
                if name in data and isinstance(value, list):
                    data[name].extend(value)
                else:
                    data[name] = value
            return object_hook(data) if object_hook else data

        config["object_pairs_hook"] = merge_duplicate_lists
        return config

    def load(self, source: "str|bytes|TextIO|Path") -> DataDict:
        try:
            data = self._load(source)
        except (json.JSONDecodeError, TypeError):
            raise ValueError(f"Invalid JSON data: {get_error_message()}")
        if not isinstance(data, dict):
            raise TypeError(f"Expected dictionary, got {type_name(data)}.")
        return data

    def _load(self, source: "str|bytes|TextIO|Path") -> object:
        if self._is_path(source):
            with open(source, encoding="UTF-8") as file:
                return json.load(file, **self.config)
        if hasattr(source, "read"):
            return json.load(source, **self.config)
        return json.loads(source, **self.config)

    def _is_path(self, source: "str|bytes|TextIO|Path") -> bool:
        if isinstance(source, Path):
            return True
        return isinstance(source, str) and "{" not in source


class JsonDumper:
    """Generic JSON dumper.

    JSON can be written to a file given as a path or as an open file object.
    If no output is given, JSON is returned as a string.

    Supports the same configuration as the underlying `json.dump`__.

    __ https://docs.python.org/3/library/json.html#json.load
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
